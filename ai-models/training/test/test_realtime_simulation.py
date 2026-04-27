import joblib
import numpy as np
import time
import random
import os
import pandas as pd
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

print("\n" + "=" * 50)
print("TEST 4: Mô phỏng real-time monitoring")
print("=" * 50)

# PATH
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "anomaly_model.pkl")

# Load model
model = joblib.load(MODEL_PATH)
print("Model loaded successfully")

print("\nĐang mô phỏng luồng dữ liệu từ cảm biến...")
print("Nhấn Ctrl+C để dừng\n")

features = ['temperature', 'humidity', 'smoke', 'co2', 'power']

try:
    for i in range(20):

        # ===== GENERATE DATA =====
        if random.random() < 0.1:
            data = [
                random.uniform(40, 50),
                random.uniform(10, 20),
                random.uniform(300, 500),
                random.uniform(800, 1200),
                random.uniform(5, 10)
            ]
        else:
            data = [
                random.uniform(22, 28),
                random.uniform(50, 70),
                random.uniform(30, 80),
                random.uniform(380, 450),
                random.uniform(30, 70)
            ]

        # ===== FIX WARNING (IMPORTANT) =====
        df_input = pd.DataFrame([data], columns=features)

        pred = model.predict(df_input)[0]
        detected = (pred == -1)

        # ===== PRINT RESULT =====
        temp, hum, smoke, co2, power = data

        if detected:
            print(f"[CẢNH BÁO] {i+1:2d}. temp={temp:.1f}°C, hum={hum:.1f}%, smoke={smoke:.0f}ppm, co2={co2:.0f}ppm, power={power:.1f}W → BẤT THƯỜNG")
        else:
            print(f"[BÌNH THƯỜNG] {i+1:2d}. temp={temp:.1f}°C, hum={hum:.1f}%, smoke={smoke:.0f}ppm, co2={co2:.0f}ppm, power={power:.1f}W")

        time.sleep(1)

except KeyboardInterrupt:
    print("\n\nDừng mô phỏng")