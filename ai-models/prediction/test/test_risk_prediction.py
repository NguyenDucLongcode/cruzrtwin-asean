"""
T-011: Test Risk Prediction Module
Kiem tra day du cac chuc nang cua module du doan rui ro.
"""

import sys
import os
import numpy as np
from datetime import datetime, timedelta

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

PASS_COUNT = 0
FAIL_COUNT = 0


def test_pass(name):
    global PASS_COUNT
    PASS_COUNT += 1
    print(f"   PASS: {name}")


def test_fail(name, detail=""):
    global FAIL_COUNT
    FAIL_COUNT += 1
    print(f"   FAIL: {name} - {detail}")


# ================== TEST 1: Model Load ==================
print("=" * 60)
print("TEST 1: Load risk model")
print("-" * 60)

try:
    from risk_predictor import RiskPredictor
    predictor = RiskPredictor()
    test_pass("RiskPredictor khoi tao thanh cong")
    test_pass(f"Model path: {predictor.model_path}")
    test_pass(f"Feature count: {len(predictor.feature_names)}")
except Exception as e:
    test_fail("Load model", str(e))
    print("Khong the tiep tuc test. Thoat.")
    sys.exit(1)

# ================== TEST 2: Predict LOW risk ==================
print("\n" + "=" * 60)
print("TEST 2: Predict LOW risk (du lieu binh thuong)")
print("-" * 60)

now = datetime.now()
normal_data = []
for i in range(30):
    normal_data.append({
        'timestamp': now - timedelta(minutes=(30 - i)),
        'temperature': 25 + np.random.normal(0, 1),
        'humidity': 65 + np.random.normal(0, 3),
        'smoke': 35 + np.random.normal(0, 5),
        'co2': 400 + np.random.normal(0, 15),
        'power': 50 + np.random.normal(0, 8)
    })

result_low = predictor.predict_risk(normal_data)

if result_low['risk_label'] == 'LOW':
    test_pass("Du lieu binh thuong -> LOW risk")
else:
    test_fail("Du lieu binh thuong", f"Expected LOW, got {result_low['risk_label']}")

if result_low['confidence'] > 0:
    test_pass(f"Confidence > 0: {result_low['confidence']}")
else:
    test_fail("Confidence", "= 0")

if 'probabilities' in result_low:
    test_pass("Co probability distribution")
else:
    test_fail("Missing probabilities")

# ================== TEST 3: Predict HIGH risk ==================
print("\n" + "=" * 60)
print("TEST 3: Predict HIGH risk (chay tiem an)")
print("-" * 60)

fire_data = []
for i in range(30):
    progress = i / 30.0
    fire_data.append({
        'timestamp': now - timedelta(minutes=(30 - i)),
        'temperature': 30 + progress * 18 + np.random.normal(0, 0.3),
        'humidity': 55 - progress * 35 + np.random.normal(0, 0.5),
        'smoke': 60 + progress * 280 + np.random.normal(0, 2),
        'co2': 420 + progress * 350 + np.random.normal(0, 5),
        'power': 50 + np.random.normal(0, 3)
    })

result_high = predictor.predict_risk(fire_data)

if result_high['risk_level'] >= 1:  # MEDIUM or HIGH
    test_pass(f"Du lieu chay -> {result_high['risk_label']} risk (MEDIUM hoac HIGH)")
else:
    test_fail("Du lieu chay", f"Expected MEDIUM/HIGH, got {result_high['risk_label']}")

if len(result_high.get('top_factors', [])) > 0:
    test_pass(f"Co top factors: {result_high['top_factors'][0]['feature']}")
else:
    test_fail("Missing top factors")

# ================== TEST 4: FIWARE Alert Format ==================
print("\n" + "=" * 60)
print("TEST 4: FIWARE Robot Alert format")
print("-" * 60)

alert = predictor.generate_robot_alert(result_high)

required_fields = ['id', 'type', 'riskLevel', 'riskScore', 'predictedFor',
                   'robotAction', 'message', 'source']

for field in required_fields:
    if field in alert:
        test_pass(f"Alert co field: {field}")
    else:
        test_fail(f"Missing field: {field}")

if alert['type'] == 'RiskAlert':
    test_pass("Entity type = RiskAlert")
else:
    test_fail("Entity type", f"Expected RiskAlert, got {alert['type']}")

if alert['id'].startswith('urn:ngsi-ld:'):
    test_pass("ID format dung NGSI-LD")
else:
    test_fail("ID format", alert['id'])

valid_actions = ['MONITOR', 'INSPECT_AREA', 'PATROL_AND_ANNOUNCE']
if alert['robotAction']['value'] in valid_actions:
    test_pass(f"Robot action hop le: {alert['robotAction']['value']}")
else:
    test_fail("Robot action", alert['robotAction']['value'])

# ================== TEST 5: Edge case - Du lieu it ==================
print("\n" + "=" * 60)
print("TEST 5: Edge case - Du lieu qua it")
print("-" * 60)

short_data = [{'timestamp': now, 'temperature': 25, 'humidity': 60,
               'smoke': 40, 'co2': 400, 'power': 50}]

result_short = predictor.predict_risk(short_data)

if result_short.get('warning'):
    test_pass(f"Tra ve warning khi du lieu it: {result_short['warning'][:50]}")
else:
    test_fail("Missing warning for short data")

if result_short['risk_label'] == 'LOW':
    test_pass("Default LOW risk khi du lieu khong du")
else:
    test_fail("Default risk", result_short['risk_label'])

# ================== TEST 6: Display ==================
print("\n" + "=" * 60)
print("TEST 6: Display prediction")
print("-" * 60)

try:
    predictor.display_prediction(result_low)
    test_pass("Display LOW risk thanh cong")
    predictor.display_prediction(result_high)
    test_pass("Display HIGH risk thanh cong")
except Exception as e:
    test_fail("Display", str(e))

# ================== SUMMARY ==================
print("\n" + "=" * 60)
print(f"KET QUA: {PASS_COUNT} PASS / {FAIL_COUNT} FAIL")
print("=" * 60)

if FAIL_COUNT == 0:
    print("TAT CA TEST PASS!")
else:
    print(f"Co {FAIL_COUNT} test FAIL. Can kiem tra lai.")
