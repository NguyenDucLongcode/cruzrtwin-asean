"""
T-011 DEMO: Risk Prediction Module
Demo 3 scenario du doan rui ro moi truong va gui alert cho Robot.
"""

import numpy as np
from datetime import datetime, timedelta
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from risk_predictor import RiskPredictor

print("=" * 70)
print("T-011 DEMO: AI ENVIRONMENTAL RISK PREDICTION")
print("   Du doan rui ro 30 phut tiep theo -> Gui canh bao Robot CRUZR")
print("=" * 70)

predictor = RiskPredictor()
now = datetime.now()
all_alerts = []

# ============================================================
# SCENARIO 1: Chay tiem an phong server
# ============================================================
print("\n" + "=" * 70)
print(" SCENARIO 1: CHAY TIEM AN - PHONG SERVER")
print("-" * 70)
print("   Mo ta: Nhiet do tang cham tu 26 -> 42 C trong 30 phut")
print("          Khoi tang tu 40 -> 200 ppm, do am giam")
print("   Ket qua mong doi: Du doan HIGH risk")
print()

scenario1_data = []
for i in range(30):
    progress = i / 30.0
    scenario1_data.append({
        'timestamp': now - timedelta(minutes=(30 - i)),
        'temperature': 26 + progress * 16 + np.random.normal(0, 0.5),
        'humidity': 65 - progress * 20 + np.random.normal(0, 1),
        'smoke': 40 + progress * 160 + np.random.normal(0, 3),
        'co2': 400 + progress * 150 + np.random.normal(0, 10),
        'power': 50 + np.random.normal(0, 5)
    })

result1 = predictor.predict_risk(scenario1_data)
predictor.display_prediction(result1)
alert1 = predictor.generate_robot_alert(result1)
all_alerts.append(alert1)

# ============================================================
# SCENARIO 2: Ro ri khi CO2 tang ham
# ============================================================
print("\n" + "=" * 70)
print(" SCENARIO 2: RO RI KHI CO2 - TANG HAM")
print("-" * 70)
print("   Mo ta: CO2 tang dan tu 400 -> 850 ppm trong 30 phut")
print("          Cac chi so khac binh thuong")
print("   Ket qua mong doi: Du doan MEDIUM -> HIGH risk")
print()

scenario2_data = []
for i in range(30):
    progress = i / 30.0
    scenario2_data.append({
        'timestamp': now - timedelta(minutes=(30 - i)),
        'temperature': 26 + np.random.normal(0, 1),
        'humidity': 65 + progress * 8 + np.random.normal(0, 2),
        'smoke': 40 + np.random.normal(0, 5),
        'co2': 400 + progress * 450 + np.random.normal(0, 10),
        'power': 50 + np.random.normal(0, 8)
    })

result2 = predictor.predict_risk(scenario2_data)
predictor.display_prediction(result2)
alert2 = predictor.generate_robot_alert(result2)
all_alerts.append(alert2)

# ============================================================
# SCENARIO 3: Hoat dong binh thuong
# ============================================================
print("\n" + "=" * 70)
print(" SCENARIO 3: HOAT DONG BINH THUONG - VAN PHONG")
print("-" * 70)
print("   Mo ta: Tat ca chi so on dinh trong gioi han binh thuong")
print("   Ket qua mong doi: Du doan LOW risk")
print()

scenario3_data = []
for i in range(30):
    scenario3_data.append({
        'timestamp': now - timedelta(minutes=(30 - i)),
        'temperature': 25 + np.random.normal(0, 1.5),
        'humidity': 65 + np.random.normal(0, 3),
        'smoke': 35 + np.random.normal(0, 5),
        'co2': 400 + np.random.normal(0, 20),
        'power': 50 + np.random.normal(0, 10)
    })

result3 = predictor.predict_risk(scenario3_data)
predictor.display_prediction(result3)
alert3 = predictor.generate_robot_alert(result3)
all_alerts.append(alert3)

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("TONG KET DEMO T-011")
print("=" * 70)

scenarios = [
    ("Chay tiem an phong server", result1),
    ("Ro ri CO2 tang ham", result2),
    ("Hoat dong binh thuong", result3)
]

print(f"\n{'Scenario':<35s} {'Risk Level':<12s} {'Confidence':<12s} {'Robot Action':<25s}")
print("-" * 84)
for name, r in scenarios:
    robot_action = predictor.ROBOT_ACTIONS[r['risk_level']]['action']
    print(f"   {name:<32s} {r['risk_label']:<12s} {r['confidence']*100:>6.1f}%      {robot_action:<25s}")

print(f"\n FIWARE ROBOT ALERTS (NGSI-v2 format):")
print("-" * 70)
for i, alert in enumerate(all_alerts, 1):
    print(f"\n   Alert {i}:")
    print(f"   ID:      {alert['id']}")
    print(f"   Risk:    {alert['riskLevel']['value']}")
    print(f"   Score:   {alert['riskScore']['value']}")
    print(f"   Action:  {alert['robotAction']['value']}")
    print(f"   Message: {alert['message']['value'][:80]}...")

print(f"\n   (Cac alert nay se duoc POST len FIWARE Orion de Robot CRUZR xu ly)")

print("\n" + "=" * 70)
print("T-011 HOAN THANH - DU DOAN RUI RO + CANH BAO ROBOT CRUZR")
print("=" * 70)
