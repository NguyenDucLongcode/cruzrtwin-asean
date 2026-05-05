"""
T-011: Generate Risk History Data
Tao du lieu time-series 3 ngay voi cac pattern rui ro thuc te.

Output: ai-models/prediction/data/risk_history.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)

# ================== PATH ==================
BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "risk_history.csv")

# ================== CONFIG ==================
TOTAL_MINUTES = 4320  # 3 ngay
START_TIME = datetime(2026, 5, 1, 0, 0, 0)

print("=" * 60)
print("T-011: GENERATE RISK HISTORY DATA")
print("=" * 60)

# ================== BASELINE DATA ==================
# Tao du lieu binh thuong lam nen
timestamps = [START_TIME + timedelta(minutes=i) for i in range(TOTAL_MINUTES)]

temperature = np.random.normal(26, 2, TOTAL_MINUTES)
humidity = np.random.normal(65, 5, TOTAL_MINUTES)
smoke = np.random.normal(40, 8, TOTAL_MINUTES)
co2 = np.random.normal(400, 25, TOTAL_MINUTES)
power = np.random.normal(50, 12, TOTAL_MINUTES)

# Mac dinh: tat ca la LOW risk
risk_level = np.zeros(TOTAL_MINUTES, dtype=int)  # 0 = LOW

# ================== PATTERN 1: CHAY TIEM AN (x3 lan) ==================
# Nhiet do + khoi tang dan trong ~60 phut truoc khi dat dinh
fire_starts = [480, 2160, 3600]  # phut 480 (8h ngay 1), 2160 (12h ngay 2), 3600 (12h ngay 3)

for fs in fire_starts:
    if fs + 90 > TOTAL_MINUTES:
        continue
    # 60 phut escalation
    for i in range(90):
        idx = fs + i
        progress = i / 90.0

        # Nhiet do tang tu 26 -> 48
        temperature[idx] = 26 + progress * 22 + np.random.normal(0, 1)
        # Khoi tang tu 40 -> 350
        smoke[idx] = 40 + progress * 310 + np.random.normal(0, 5)
        # Do am giam
        humidity[idx] = 65 - progress * 30 + np.random.normal(0, 2)
        # CO2 tang nhe
        co2[idx] = 400 + progress * 200 + np.random.normal(0, 10)

        # Label: 30 phut dau = MEDIUM, 60 phut sau = HIGH
        if progress < 0.33:
            risk_level[idx] = 1  # MEDIUM
        else:
            risk_level[idx] = 2  # HIGH

    # 30 phut TRUOC khi bat dau escalation cung la MEDIUM (canh bao som)
    for i in range(30):
        pre_idx = fs - 30 + i
        if 0 <= pre_idx < TOTAL_MINUTES:
            # Nhiet do hoi tang nhe
            temperature[pre_idx] = 26 + (i / 30.0) * 3 + np.random.normal(0, 0.5)
            smoke[pre_idx] = 40 + (i / 30.0) * 15 + np.random.normal(0, 2)
            risk_level[pre_idx] = 1  # MEDIUM

# ================== PATTERN 2: RO RI KHI CO2 (x2 lan) ==================
co2_starts = [1200, 3000]  # phut 1200 (20h ngay 1), 3000 (2h ngay 3)

for cs in co2_starts:
    if cs + 120 > TOTAL_MINUTES:
        continue
    for i in range(120):
        idx = cs + i
        progress = i / 120.0

        # CO2 tang tu tu 400 -> 1100
        co2[idx] = 400 + progress * 700 + np.random.normal(0, 15)
        # Do am tang nhe (do nuoc ngung tu)
        humidity[idx] = 65 + progress * 15 + np.random.normal(0, 2)

        if progress < 0.4:
            risk_level[idx] = 1  # MEDIUM
        else:
            risk_level[idx] = 2  # HIGH

    # 20 phut truoc: MEDIUM
    for i in range(20):
        pre_idx = cs - 20 + i
        if 0 <= pre_idx < TOTAL_MINUTES:
            co2[pre_idx] = 400 + (i / 20.0) * 50 + np.random.normal(0, 5)
            risk_level[pre_idx] = 1

# ================== PATTERN 3: THIET BI QUA TAI (x4 lan) ==================
power_starts = [720, 1800, 2880, 4000]

for ps in power_starts:
    if ps + 60 > TOTAL_MINUTES:
        continue
    for i in range(60):
        idx = ps + i
        progress = i / 60.0

        # Power dao dong manh + tang
        power[idx] = 50 + progress * 80 + np.random.normal(0, 15)
        # Nhiet do tang nhe do thiet bi nong
        temperature[idx] = 26 + progress * 8 + np.random.normal(0, 1)

        if progress < 0.5:
            risk_level[idx] = 1  # MEDIUM
        else:
            risk_level[idx] = 2  # HIGH

# ================== CLIP VALUES ==================
temperature = np.clip(temperature, 15, 55)
humidity = np.clip(humidity, 5, 99)
smoke = np.clip(smoke, 0, 600)
co2 = np.clip(co2, 200, 1500)
power = np.clip(power, 0, 200)

# ================== BUILD DATAFRAME ==================
df = pd.DataFrame({
    'timestamp': timestamps,
    'temperature': np.round(temperature, 2),
    'humidity': np.round(humidity, 2),
    'smoke': np.round(smoke, 2),
    'co2': np.round(co2, 2),
    'power': np.round(power, 2),
    'risk_level': risk_level
})

# ================== SAVE ==================
df.to_csv(OUTPUT_FILE, index=False)

# ================== SUMMARY ==================
counts = df['risk_level'].value_counts().sort_index()
print(f"\nDa tao file: {OUTPUT_FILE}")
print(f"Tong so mau: {len(df)}")
print(f"\nPhan bo risk level:")
print(f"   LOW    (0): {counts.get(0, 0)} mau ({counts.get(0, 0)/len(df)*100:.1f}%)")
print(f"   MEDIUM (1): {counts.get(1, 0)} mau ({counts.get(1, 0)/len(df)*100:.1f}%)")
print(f"   HIGH   (2): {counts.get(2, 0)} mau ({counts.get(2, 0)/len(df)*100:.1f}%)")
print(f"\nPatterns:")
print(f"   - Chay tiem an: 3 su kien (90 phut/su kien)")
print(f"   - Ro ri CO2:    2 su kien (120 phut/su kien)")
print(f"   - Qua tai dien: 4 su kien (60 phut/su kien)")
print(f"\n5 dong dau:")
print(df.head().to_string(index=False))
