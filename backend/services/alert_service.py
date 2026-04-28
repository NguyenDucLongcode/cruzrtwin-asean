from datetime import datetime
import httpx
from typing import Dict, Any
from collections import deque
import requests
from services.classify_anomaly import classify_anomaly
from pathlib import Path
import joblib
import pandas as pd




# Xử lý alert từ FIWARE webhook, broadcast WebSocket, gửi robot
# Robot API URL (T-14 sẽ chạy ở port 8001)
ROBOT_API_URL = "http://127.0.0.1:8001/api/robot/alert"
ALERT_HISTORY_LIMIT = 200
_ALERT_HISTORY = deque(maxlen=ALERT_HISTORY_LIMIT)
_model = None  # Biến toàn cục để cache AI model
# Thêm debounce dictionary
_last_alert_sent = {}



# ==================== HELPER FUNCTIONS ====================

def _project_root() -> Path:
    """Lấy thư mục gốc của project (cruzrtwin-asean)"""
    return Path(__file__).resolve().parents[2]

def _resolve_anomaly_model_path() -> Path:
    """Tìm đường dẫn đến anomaly_model.pkl ở nhiều vị trí"""
    root = _project_root()
    candidates = [
        root / "ai-models" / "models" / "anomaly_model.pkl",
        root / "ai-models" / "training" / "models" / "anomaly_model.pkl",
        root / "anomaly_model.pkl",
    ]
    for path in candidates:
        if path.exists():
            print(f"✅ Found model at: {path}")
            return path
    raise FileNotFoundError("anomaly_model.pkl not found in expected paths")


# Helper function để load AI model (nếu có), sử dụng joblib
def get_model():
    global _model
    if _model is None:
        model_path = _resolve_anomaly_model_path()
        _model = joblib.load(model_path)
        print(f"AI model loaded from {model_path}")
    return _model

_sensor_cache = {
    "temperature": {"value": 25, "timestamp": None},   # từ TemperatureSensor
    "humidity": {"value": 60, "timestamp": None},      # từ HumiditySensor
    "smoke": {"value": 0, "timestamp": None},          # từ SmokeSensor (smokeLevel)
    "co2": {"value": 400, "timestamp": None},          # từ AirQualitySensor
    "power": {"value": 50, "timestamp": None}          # từ SmartPlug
}

# Hàm phân loại bất thường, trả về True nếu là anomaly (dựa trên AI model)
def is_anomaly(temp, humidity, smoke, co2, power):
    """Kiểm tra có bất thường hay không dùng AI model"""
    model = get_model()
    features = pd.DataFrame([[temp, humidity, smoke, co2, power]], 
                            columns=['temperature', 'humidity', 'smoke', 'co2', 'power'])
    prediction = model.predict(features)[0]
    return prediction == -1


# Hàm phân loại loại bất thường và mức độ nghiêm trọng (rule-based)
def store_alert(alert: Dict[str, Any]):
    """Lưu alert vào bộ nhớ tạm để API có thể truy vấn nhanh."""
    _ALERT_HISTORY.append(dict(alert))


def get_recent_alerts(limit: int = 20) -> list:
    """Lấy danh sách alert gần nhất (oldest -> newest)."""
    safe_limit = max(1, min(limit, ALERT_HISTORY_LIMIT))
    items = list(_ALERT_HISTORY)
    return items[-safe_limit:]


def get_latest_alert() -> Dict[str, Any] | None:
    """Lấy alert mới nhất, trả về None nếu chưa có dữ liệu."""
    if not _ALERT_HISTORY:
        return None
    return dict(_ALERT_HISTORY[-1])

# Helper function để đảm bảo text an toàn cho console (tránh lỗi encoding)
def _safe_console_text(text: str) -> str:
    """Return a console-safe version of text for non-UTF8 terminals."""
    return text.encode("ascii", errors="replace").decode("ascii")


def _print_safe(text: str):
    print(_safe_console_text(text), flush=True)

# Gửi alert qua WebSocket đến dashboard
async def broadcast_alert(alert: Dict):
    """Broadcast alert qua WebSocket đến dashboard"""
    from services.websocket_manager import manager
    await manager.broadcast(alert)

# Gửi alert đến robot queue (T-14 sẽ nhận lệnh navigation)
async def send_to_robot_queue(alert: Dict):
    """
    Gửi alert đến robot queue (cho T-14)
    Robot sẽ nhận lệnh navigation đến khu vực có vấn đề
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(ROBOT_API_URL, json=alert, timeout=3.0)
            if 200 <= response.status_code < 300:
                print(f"   [ROBOT] Forwarded to robot queue (status={response.status_code})", flush=True)
                try:
                    robot_body = response.json()
                    print(f"   [ROBOT] Response: {robot_body}", flush=True)
                except Exception:
                    print(f"   [ROBOT] Response text: {response.text}", flush=True)
                return True

            print(f"   [WARN] Robot API responded non-2xx (status={response.status_code})", flush=True)
            print(f"   [WARN] Robot response: {response.text}", flush=True)
            return False
    except Exception as exc:
        print(f"   [WARN] Robot API not available: {type(exc).__name__}: {exc}", flush=True)
        return False
    
# ------------WEBHOOK HANDLER CHÍNH------------
async def process_anomaly_alert(payload: Dict) -> list:
    alerts = []
    now = datetime.now()

    for notification in payload.get('data', []):
        device_id = notification.get('id')

        now = datetime.now()

        # Cập nhật cache sensor (dựa trên entity type và attributes)
        if 'temperature' in notification:
            _sensor_cache['temperature']['value'] = notification['temperature']['value']
            _sensor_cache['temperature']['timestamp'] = now

        if 'humidity' in notification:
            _sensor_cache['humidity']['value'] = notification['humidity']['value']
            _sensor_cache['humidity']['timestamp'] = now

        if 'smokeLevel' in notification:
            _sensor_cache['smoke']['value'] = notification['smokeLevel']['value']
            _sensor_cache['smoke']['timestamp'] = now

        if 'co2' in notification:
            _sensor_cache['co2']['value'] = notification['co2']['value']
            _sensor_cache['co2']['timestamp'] = now

        if 'power' in notification:
            _sensor_cache['power']['value'] = notification['power']['value']
            _sensor_cache['power']['timestamp'] = now

        # In ra console để debug nhanh (đảm bảo an toàn encoding)
        temp = _sensor_cache['temperature']['value'] 
        humidity = _sensor_cache['humidity']['value']
        smoke = _sensor_cache['smoke']['value']
        co2 = _sensor_cache['co2']['value']
        power = _sensor_cache['power']['value']

        _print_safe(f"\n  STATE [{device_id}]")
        _print_safe(f"   Temp={temp}, Humidity={humidity}, Smoke={smoke}, CO2={co2}, Power={power}")

         # ===== DEBOUNCE: Chỉ xử lý nếu đã qua 30 giây =====
        alert_key = f"{device_id}_{temp}_{smoke}_{co2}"
        last_time = _last_alert_sent.get(alert_key)

        if last_time and (now - last_time).seconds < 30:
            print(f"   Skip {device_id} (debounce 30s)")
            continue

        # ===== AI CHECK =====
        anomaly = is_anomaly(temp, humidity, smoke, co2, power)

        if not anomaly:
            _print_safe("   AI: Binh thuong -> skip")
            continue

        _print_safe("   AI: BAT THUONG detected!")

        # ===== RULE-BASED CLASSIFY =====
        classification = classify_anomaly(temp, humidity, smoke, co2, power)

        _print_safe(f"   Type: {classification['type']} ({classification['severity']})")

        if classification['severity'] != "none":
            alert_data = {
                "message": classification['message'],
                "severity": classification['severity'],
                "type": classification['type'],
                "action": classification['action'],
                "instruction": classification['robot_instruction'],
                "device_id": device_id,
                "timestamp": now.isoformat()
            }

            alert_data["robot_forwarded"] = await send_to_robot_queue(alert_data)
            store_alert(alert_data)
            alerts.append(alert_data)
        else:
            _print_safe("   Khong can goi robot")

    return alerts