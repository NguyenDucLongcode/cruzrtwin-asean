"""
T-011: Risk Predictor Module
Module chinh du doan rui ro moi truong va gui canh bao FIWARE cho Robot.

Chuc nang:
  - predict_risk(): Du doan risk level tu sensor data 30 phut gan nhat
  - display_prediction(): Hien thi ket qua len console (co mau sac)
  - generate_robot_alert(): Tao FIWARE NGSI-v2 entity canh bao cho Robot CRUZR
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import os
import warnings
warnings.filterwarnings('ignore')


class RiskPredictor:
    """Module du doan rui ro moi truong dua tren du lieu sensor qua khu."""

    RISK_LABELS = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}
    RISK_ICONS = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}
    RISK_COLORS = {0: "green", 1: "yellow", 2: "red"}

    # Robot action mapping
    ROBOT_ACTIONS = {
        0: {"action": "MONITOR", "description": "Robot tiep tuc giam sat binh thuong"},
        1: {"action": "INSPECT_AREA", "description": "Robot di chuyen den khu vuc kiem tra"},
        2: {"action": "PATROL_AND_ANNOUNCE", "description": "Robot tuan tra + phat canh bao bang giong noi"}
    }

    SENSOR_FEATURES = ['temperature', 'humidity', 'smoke', 'co2', 'power']

    def __init__(self, model_path=None):
        """Khoi tao Risk Predictor."""
        resolved_path = self._resolve_model_path(model_path)
        model_data = joblib.load(resolved_path)

        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        self.window_size = model_data.get('window_size', 30)
        self.metrics = model_data.get('metrics', {})
        self.model_path = resolved_path

        # Load anomaly model (optional, for feature extraction)
        self.anomaly_model = self._load_anomaly_model()

        print("=" * 60)
        print("T-011: RISK PREDICTION MODULE")
        print(f"   Model loaded: {os.path.basename(self.model_path)}")
        print(f"   Window size: {self.window_size} phut")
        print(f"   Train F1-Score: {self.metrics.get('f1_score', 'N/A')}")
        print(f"   Risk levels: LOW / MEDIUM / HIGH")
        print("=" * 60)

    def _resolve_model_path(self, model_path):
        """Tim file model risk_model.pkl."""
        base_dir = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))

        candidates = []
        if model_path:
            if os.path.isabs(model_path):
                candidates.append(model_path)
            else:
                candidates.append(os.path.join(base_dir, model_path))
                candidates.append(os.path.join(project_root, model_path))

        candidates.extend([
            os.path.join(base_dir, "models", "risk_model.pkl"),
            os.path.join(project_root, "ai-models", "prediction", "models", "risk_model.pkl"),
        ])

        for c in candidates:
            normalized = os.path.abspath(c)
            if os.path.exists(normalized):
                return normalized

        searched = "\n".join(f"- {os.path.abspath(p)}" for p in candidates)
        raise FileNotFoundError(
            "Khong tim thay risk_model.pkl. Da kiem tra:\n"
            f"{searched}\n"
            "Hay chay: python ai-models/prediction/train_risk_model.py"
        )

    def _load_anomaly_model(self):
        """Load anomaly model T-07 (optional)."""
        base_dir = os.path.dirname(__file__)
        paths = [
            os.path.join(base_dir, "..", "training", "models", "anomaly_model.pkl"),
            os.path.join(base_dir, "..", "..", "anomaly_model.pkl"),
        ]
        for p in paths:
            if os.path.exists(p):
                return joblib.load(p)
        return None

    def _count_anomalies(self, window_data):
        """Dem anomaly trong window."""
        if self.anomaly_model is None:
            count = 0
            for _, row in window_data.iterrows():
                if (row['temperature'] > 35 or row['smoke'] > 100 or
                    row['co2'] > 600 or row['power'] > 100 or row['humidity'] < 30):
                    count += 1
            return count

        features_df = window_data[self.SENSOR_FEATURES].copy()
        preds = self.anomaly_model.predict(features_df)
        return int(np.sum(preds == -1))

    def _compute_trend(self, values):
        """Tinh slope (xu huong)."""
        if len(values) < 2:
            return 0.0
        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)
        return float(coeffs[0])

    def _extract_features(self, window_data):
        """Trich xuat features tu window 30 phut."""
        features = {}

        anomaly_count = self._count_anomalies(window_data)
        features['anomaly_count'] = anomaly_count
        features['anomaly_rate'] = anomaly_count / len(window_data)

        temp = window_data['temperature'].values
        features['temp_mean'] = np.mean(temp)
        features['temp_max'] = np.max(temp)
        features['temp_std'] = np.std(temp)
        features['temp_trend'] = self._compute_trend(temp)

        hum = window_data['humidity'].values
        features['humidity_mean'] = np.mean(hum)
        features['humidity_min'] = np.min(hum)
        features['humidity_trend'] = self._compute_trend(hum)

        smk = window_data['smoke'].values
        features['smoke_mean'] = np.mean(smk)
        features['smoke_max'] = np.max(smk)
        features['smoke_std'] = np.std(smk)
        features['smoke_trend'] = self._compute_trend(smk)

        c = window_data['co2'].values
        features['co2_mean'] = np.mean(c)
        features['co2_max'] = np.max(c)
        features['co2_trend'] = self._compute_trend(c)

        pwr = window_data['power'].values
        features['power_mean'] = np.mean(pwr)
        features['power_max'] = np.max(pwr)
        features['power_std'] = np.std(pwr)
        features['power_trend'] = self._compute_trend(pwr)

        return features

    def predict_risk(self, sensor_history):
        """
        Du doan muc do rui ro trong 30 phut tiep theo.

        Args:
            sensor_history: list of dict hoac DataFrame,
                            moi dict co keys: timestamp, temperature, humidity, smoke, co2, power
                            Can it nhat 5 mau (khuyen nghi 30 mau = 30 phut).

        Returns:
            dict: Ket qua du doan gom risk_level, risk_score, top_factors, v.v.
        """
        if isinstance(sensor_history, list):
            df = pd.DataFrame(sensor_history)
        else:
            df = sensor_history.copy()

        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Lay toi da window_size mau gan nhat
        if len(df) > self.window_size:
            df = df.tail(self.window_size)

        if len(df) < 5:
            return {
                'risk_level': 0,
                'risk_label': 'LOW',
                'risk_score': 0.0,
                'confidence': 0.0,
                'warning': 'Khong du du lieu (can it nhat 5 mau)',
                'top_factors': [],
                'prediction_time': datetime.now().isoformat(),
                'predicted_for': (datetime.now() + timedelta(minutes=30)).isoformat()
            }

        # Extract features
        features = self._extract_features(df)
        X = pd.DataFrame([features])[self.feature_names]

        # Predict
        risk_level = int(self.model.predict(X)[0])
        probabilities = self.model.predict_proba(X)[0]

        risk_score = float(probabilities[risk_level])

        # Top contributing factors
        importances = self.model.feature_importances_
        feature_contributions = []
        for i, fname in enumerate(self.feature_names):
            feature_contributions.append({
                'feature': fname,
                'importance': float(importances[i]),
                'value': float(features[fname])
            })
        feature_contributions.sort(key=lambda x: x['importance'], reverse=True)

        now = datetime.now()
        result = {
            'risk_level': risk_level,
            'risk_label': self.RISK_LABELS[risk_level],
            'risk_score': round(risk_score, 4),
            'confidence': round(float(max(probabilities)), 4),
            'probabilities': {
                'LOW': round(float(probabilities[0]), 4),
                'MEDIUM': round(float(probabilities[1]), 4),
                'HIGH': round(float(probabilities[2]), 4)
            },
            'top_factors': feature_contributions[:5],
            'window_stats': {
                'samples_analyzed': len(df),
                'temp_current': round(float(df['temperature'].iloc[-1]), 2),
                'smoke_current': round(float(df['smoke'].iloc[-1]), 2),
                'co2_current': round(float(df['co2'].iloc[-1]), 2),
                'power_current': round(float(df['power'].iloc[-1]), 2),
            },
            'prediction_time': now.isoformat(),
            'predicted_for': (now + timedelta(minutes=30)).isoformat()
        }

        return result

    def display_prediction(self, result):
        """Hien thi ket qua du doan len console."""
        level = result['risk_level']
        label = result['risk_label']

        # Risk level display
        if level == 0:
            icon = "[LOW]"
            bar = "====="
        elif level == 1:
            icon = "[MEDIUM]"
            bar = "==============="
        else:
            icon = "[HIGH]"
            bar = "========================="

        print()
        print("+" + "-" * 58 + "+")
        print("|  DU BAO RUI RO MOI TRUONG - 30 PHUT TIEP THEO           |")
        print("+" + "-" * 58 + "+")
        print(f"|                                                          |")
        print(f"|   Muc rui ro:  {icon:<10s}                               |")
        print(f"|   Risk bar:    [{bar:<25s}]              |")
        print(f"|   Confidence:  {result['confidence']*100:.1f}%                                  |")
        print(f"|                                                          |")
        print(f"|   Xac suat:                                              |")
        print(f"|     LOW:    {result['probabilities']['LOW']*100:6.2f}%                                  |")
        print(f"|     MEDIUM: {result['probabilities']['MEDIUM']*100:6.2f}%                                  |")
        print(f"|     HIGH:   {result['probabilities']['HIGH']*100:6.2f}%                                  |")
        print(f"|                                                          |")

        # Current readings
        stats = result.get('window_stats', {})
        if stats:
            print(f"|   Sensor hien tai:                                       |")
            print(f"|     Nhiet do: {stats.get('temp_current', 0):>6.1f} C                                |")
            print(f"|     Khoi:     {stats.get('smoke_current', 0):>6.1f} ppm                              |")
            print(f"|     CO2:      {stats.get('co2_current', 0):>6.1f} ppm                              |")
            print(f"|     Dien:     {stats.get('power_current', 0):>6.1f} W                                |")

        print(f"|                                                          |")

        # Top factors
        print(f"|   Top yeu to anh huong:                                  |")
        for i, factor in enumerate(result.get('top_factors', [])[:3], 1):
            fname = factor['feature'][:18]
            imp = factor['importance']
            print(f"|     {i}. {fname:<18s} (weight: {imp:.4f})              |")

        # Robot action
        robot = self.ROBOT_ACTIONS.get(level, self.ROBOT_ACTIONS[0])
        print(f"|                                                          |")
        print(f"|   Robot Action: {robot['action']:<40s} |")
        print(f"|   -> {robot['description']:<52s}|")

        print(f"|                                                          |")
        print(f"|   Thoi diem du doan: {result['prediction_time'][:19]:<36s} |")
        print(f"|   Du bao cho:        {result['predicted_for'][:19]:<36s} |")
        print("+" + "-" * 58 + "+")

        if result.get('warning'):
            print(f"\n   WARNING: {result['warning']}")

    def generate_robot_alert(self, result):
        """
        Tao FIWARE NGSI-v2 entity canh bao gui cho Robot CRUZR.

        Returns:
            dict: FIWARE entity format
        """
        level = result['risk_level']
        label = result['risk_label']
        robot = self.ROBOT_ACTIONS.get(level, self.ROBOT_ACTIONS[0])

        # Tao message canh bao cho robot
        messages = {
            0: "Moi truong on dinh. Tiep tuc giam sat.",
            1: f"Canh bao: Phat hien dau hieu bat thuong. "
               f"Yeu to chinh: {result['top_factors'][0]['feature'] if result['top_factors'] else 'N/A'}. "
               f"De nghi kiem tra khu vuc.",
            2: f"CANH BAO KHAN CAP: Rui ro cao! "
               f"Yeu to chinh: {result['top_factors'][0]['feature'] if result['top_factors'] else 'N/A'}. "
               f"Robot tuan tra va phat canh bao ngay lap tuc!"
        }

        alert_entity = {
            "id": f"urn:ngsi-ld:RiskAlert:alert_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "type": "RiskAlert",
            "TimeInstant": {
                "type": "DateTime",
                "value": result['prediction_time'],
                "metadata": {}
            },
            "riskLevel": {
                "type": "Text",
                "value": label,
                "metadata": {}
            },
            "riskScore": {
                "type": "Number",
                "value": result['risk_score'],
                "metadata": {}
            },
            "predictedFor": {
                "type": "DateTime",
                "value": result['predicted_for'],
                "metadata": {}
            },
            "probabilities": {
                "type": "StructuredValue",
                "value": result['probabilities'],
                "metadata": {}
            },
            "topFactors": {
                "type": "StructuredValue",
                "value": [
                    {"feature": f['feature'], "importance": round(f['importance'], 4)}
                    for f in result.get('top_factors', [])[:5]
                ],
                "metadata": {}
            },
            "robotAction": {
                "type": "Text",
                "value": robot['action'],
                "metadata": {
                    "description": {
                        "value": robot['description']
                    }
                }
            },
            "message": {
                "type": "Text",
                "value": messages.get(level, messages[0]),
                "metadata": {}
            },
            "sensorSnapshot": {
                "type": "StructuredValue",
                "value": result.get('window_stats', {}),
                "metadata": {}
            },
            "source": {
                "type": "Text",
                "value": "T-011_Risk_Predictor",
                "metadata": {}
            }
        }

        return alert_entity


# ================== STANDALONE TEST ==================
if __name__ == "__main__":
    print("\nTESTING RISK PREDICTOR MODULE\n")

    predictor = RiskPredictor()

    # Test voi du lieu binh thuong
    now = datetime.now()
    normal_data = []
    for i in range(30):
        normal_data.append({
            'timestamp': now - timedelta(minutes=(30 - i)),
            'temperature': 25 + np.random.normal(0, 1),
            'humidity': 65 + np.random.normal(0, 3),
            'smoke': 35 + np.random.normal(0, 5),
            'co2': 400 + np.random.normal(0, 20),
            'power': 50 + np.random.normal(0, 10)
        })

    result = predictor.predict_risk(normal_data)
    predictor.display_prediction(result)

    alert = predictor.generate_robot_alert(result)
    print(f"\nFIWARE Robot Alert Entity:")
    print(f"   ID:     {alert['id']}")
    print(f"   Risk:   {alert['riskLevel']['value']}")
    print(f"   Action: {alert['robotAction']['value']}")

    print("\nMODULE HOAT DONG DUNG!")
