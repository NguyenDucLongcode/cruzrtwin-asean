import joblib
import numpy as np
import pandas as pd  # Thêm dòng này
import os

print("=" * 50)
print("TEST 1: Kiểm tra model hoạt động")
print("=" * 50)

# FIX PATH CHUẨN
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR,"models", "anomaly_model.pkl")

# Load model
model = joblib.load(MODEL_PATH)
print("Model loaded successfully")

# Định nghĩa tên cột (quan trọng để hết warning)
feature_names = ['temperature', 'humidity', 'smoke', 'co2', 'power']

# Test cases
test_cases = [
    ([25, 60, 50, 400, 50], "Phòng bình thường"),
    ([45, 15, 400, 1000, 8], "CHÁY (nhiệt cao, khói cao)"),
    ([30, 80, 300, 800, 30], "Cảnh báo (khói cao)"),
    ([22, 55, 30, 380, 10], "Đêm khuya (ít hoạt động)"),
    ([35, 20, 500, 1200, 5], "KHẨN CẤP (nguy hiểm)"),
]

print("\nKết quả dự đoán:")
for data, description in test_cases:
    # Chuyển list thành DataFrame có tên cột
    df = pd.DataFrame([data], columns=feature_names)
    pred = model.predict(df)[0]
    result = "🔴 BẤT THƯỜNG" if pred == -1 else "🟢 BÌNH THƯỜNG"
    temp, hum, smoke, co2, power = data
    print(f"   {result} | {description}")
    print(f"        → temp={temp}°C, hum={hum}%, smoke={smoke}ppm, co2={co2}ppm, power={power}W")
    print()