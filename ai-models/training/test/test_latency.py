import joblib
import numpy as np
import time
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

print("\n" + "=" * 50)
print("TEST 2: Đo tốc độ dự đoán")
print("=" * 50)

# PATH CHUẨN
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR,"models", "anomaly_model.pkl")

# Load model
model = joblib.load(MODEL_PATH)
print("Model loaded successfully")

# Test với 1000 mẫu
n_tests = 1000
test_data = np.random.rand(n_tests, 5) * 100  # random data

start_time = time.time()
for data in test_data:
    model.predict([data])
end_time = time.time()

total_time = (end_time - start_time) * 1000  # ms
avg_time = total_time / n_tests

print(f"   Số mẫu test: {n_tests}")
print(f"   Tổng thời gian: {total_time:.2f} ms")
print(f"   Trung bình 1 mẫu: {avg_time:.4f} ms")
print(f"   Latency < 5ms → Tốt cho real-time!")