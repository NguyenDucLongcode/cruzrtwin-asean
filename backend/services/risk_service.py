from typing import List
from pathlib import Path

import pandas as pd
import joblib

from models import SensorData, RiskScore
from config import ALERT_THRESHOLD_TEMP, ALERT_THRESHOLD_SMOKE, ALERT_THRESHOLD_CO2

_ANOMALY_MODEL = None
_ANOMALY_MODEL_LOAD_ERROR = None
_FEATURE_COLUMNS = ["temperature", "humidity", "smoke", "co2", "power"]


# Helper function để lấy root của project, dùng để tìm file AI model/optimizer
def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


# Helper function để resolve đường dẫn đến anomaly_model.pkl, hỗ trợ cả khi chạy từ root hay từ backend/
def _resolve_anomaly_model_path() -> Path:
    root = _project_root()
    candidates = [
        root / "ai-models" / "training" / "models" / "anomaly_model.pkl",
        root / "anomaly_model.pkl",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("anomaly_model.pkl not found in expected paths")


# Helper function để load AI anomaly detection model từ file, nếu có
def _get_anomaly_model():
    global _ANOMALY_MODEL, _ANOMALY_MODEL_LOAD_ERROR
    if _ANOMALY_MODEL is not None:
        return _ANOMALY_MODEL
    if _ANOMALY_MODEL_LOAD_ERROR is not None:
        return None

    try:
        model_path = _resolve_anomaly_model_path()
        _ANOMALY_MODEL = joblib.load(model_path)
        return _ANOMALY_MODEL
    except Exception as exc:
        _ANOMALY_MODEL_LOAD_ERROR = str(exc)
        return None


# Helper function để tạo message alert dựa trên loại entity và dữ liệu bất thường
def _predict_anomaly(sensor_data: SensorData):
    model = _get_anomaly_model()
    if model is None:
        return None

    sample = pd.DataFrame([
        {
            "temperature": sensor_data.temperature if sensor_data.temperature is not None else 25.0,
            "humidity": sensor_data.humidity if sensor_data.humidity is not None else 60.0,
            "smoke": sensor_data.smokeLevel if sensor_data.smokeLevel is not None else 50.0,
            "co2": sensor_data.co2 if sensor_data.co2 is not None else 400.0,
            "power": sensor_data.power if sensor_data.power is not None else 10.0,
        }
    ], columns=_FEATURE_COLUMNS)

    pred = model.predict(sample)[0]
    return pred == -1

# Tính risk score dựa trên dữ liệu cảm biến, kết hợp rule-based và 
# AI model để đánh giá mức độ rủi ro. AI model sẽ giúp phát hiện các mẫu dữ liệu
def calculate_risk_score(sensor_data: SensorData) -> RiskScore:
    """Tính risk score dựa trên dữ liệu cảm biến"""
    risk = 0
    reasons = []
    
    if sensor_data.temperature:
        if sensor_data.temperature > ALERT_THRESHOLD_TEMP:
            risk += 40
            reasons.append(f"Nhiệt độ cao: {sensor_data.temperature}°C")
        elif sensor_data.temperature > 30:
            risk += 15
            reasons.append(f"Nhiệt độ: {sensor_data.temperature}°C")
    
    if sensor_data.smokeLevel:
        if sensor_data.smokeLevel > ALERT_THRESHOLD_SMOKE:
            risk += 50
            reasons.append(f"Khói cao: {sensor_data.smokeLevel}ppm")
        elif sensor_data.smokeLevel > 100:
            risk += 20
            reasons.append(f"Khói: {sensor_data.smokeLevel}ppm")
    
    if sensor_data.co2 and sensor_data.co2 > ALERT_THRESHOLD_CO2:
        risk += 30
        reasons.append(f"CO2 cao: {sensor_data.co2}ppm")
    
    if sensor_data.aqi and sensor_data.aqi > 100:
        risk += 20
        reasons.append(f"AQI: {sensor_data.aqi}")

    ai_anomaly = _predict_anomaly(sensor_data)
    if ai_anomaly is True:
        risk += 30
        reasons.append("AI model phát hiện mẫu dữ liệu bất thường")
    elif ai_anomaly is None:
        reasons.append("AI model chưa sẵn sàng, đang dùng rule-based")
    
    risk = min(risk, 100)
    
    if risk >= 70:
        level = "critical"
    elif risk >= 40:
        level = "high"
    elif risk >= 20:
        level = "medium"
    else:
        level = "low"
    
    return RiskScore(score=risk, level=level, reasons=reasons)