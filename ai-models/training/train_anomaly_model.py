import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import time
import os

# ================== PATH ==================
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR,"data", "sensor_data.csv")
MODEL_PATH = os.path.join(BASE_DIR,"models", "anomaly_model.pkl")

# ================== LOAD DATA ==================
print("Đang đọc dữ liệu từ:", DATA_PATH)

df = pd.read_csv(DATA_PATH)

features = ['temperature', 'humidity', 'smoke', 'co2', 'power']
X = df[features]
y_true = df['label']

print(f"Dữ liệu: {len(df)} mẫu, {len(features)} đặc trưng")

# ================== TRAIN MODEL ==================
print("\nĐang train Isolation Forest...")

start_time = time.time()

model = IsolationForest(
    contamination=0.05,
    random_state=42,
    n_estimators=100
)

model.fit(X)

train_time = time.time() - start_time
print(f"Train xong trong {train_time*1000:.2f} ms")

# ================== PREDICT ==================
y_pred = model.predict(X)
y_pred = np.where(y_pred == -1, 1, 0)

# ================== EVALUATE ==================
acc = accuracy_score(y_true, y_pred)
prec = precision_score(y_true, y_pred)
rec = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)

print("\n  Kết quả:")
print(f"   Accuracy:  {acc:.4f}")
print(f"   Precision: {prec:.4f}")
print(f"   Recall:    {rec:.4f}")
print(f"   F1-Score:  {f1:.4f}")

# ================== SAVE MODEL ==================
joblib.dump(model, MODEL_PATH)
print(f"\nĐã lưu model tại: {MODEL_PATH}")

# ================== TEST (FIX WARNING) ==================
print("\nTest thử model:")

# DÙNG DataFrame để tránh warning sklearn
sample_normal = pd.DataFrame([[25, 60, 50, 400, 50]], columns=features)
sample_anomaly = pd.DataFrame([[45, 15, 400, 1000, 8]], columns=features)

pred_normal = model.predict(sample_normal)
pred_anomaly = model.predict(sample_anomaly)

def label(x):
    return "BẤT THƯỜNG" if x == -1 else "BÌNH THƯỜNG"

print(f"   Normal  → {label(pred_normal[0])}")
print(f"   Anomaly → {label(pred_anomaly[0])}")