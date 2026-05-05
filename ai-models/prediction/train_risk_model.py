"""
T-011: Train Risk Prediction Model
Trich xuat sliding window features tu du lieu time-series va train Random Forest.

Input:  ai-models/prediction/data/risk_history.csv
Output: ai-models/prediction/models/risk_model.pkl
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import joblib
import time
import os
import warnings
warnings.filterwarnings('ignore')

# ================== PATH ==================
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "data", "risk_history.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "risk_model.pkl")

# Load anomaly model tu T-07 (de dem anomaly trong window)
ANOMALY_MODEL_PATHS = [
    os.path.join(BASE_DIR, "..", "training", "models", "anomaly_model.pkl"),
    os.path.join(BASE_DIR, "..", "..", "anomaly_model.pkl"),
]
anomaly_model = None
for amp in ANOMALY_MODEL_PATHS:
    if os.path.exists(amp):
        anomaly_model = joblib.load(amp)
        print(f"Loaded anomaly model T-07: {os.path.abspath(amp)}")
        break

if anomaly_model is None:
    print("WARNING: Khong tim thay anomaly_model.pkl. Se dung rule-based thay ML.")

# ================== CONFIG ==================
WINDOW_SIZE = 30  # 30 phut
STEP_SIZE = 5     # Buoc truot 5 phut

RISK_LABELS = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}
SENSOR_FEATURES = ['temperature', 'humidity', 'smoke', 'co2', 'power']

print("=" * 60)
print("T-011: TRAIN RISK PREDICTION MODEL")
print("=" * 60)

# ================== LOAD DATA ==================
print(f"\nDoc du lieu tu: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)
df['timestamp'] = pd.to_datetime(df['timestamp'])
print(f"Tong so mau: {len(df)}")

# ================== FEATURE EXTRACTION ==================
def count_anomalies(window_data):
    """Dem so mau bat thuong trong window dung model T-07."""
    if anomaly_model is None:
        # Fallback: rule-based
        count = 0
        for _, row in window_data.iterrows():
            if (row['temperature'] > 35 or row['smoke'] > 100 or
                row['co2'] > 600 or row['power'] > 100 or row['humidity'] < 30):
                count += 1
        return count

    features = window_data[SENSOR_FEATURES].values
    features_df = pd.DataFrame(features, columns=SENSOR_FEATURES)
    preds = anomaly_model.predict(features_df)
    return int(np.sum(preds == -1))


def compute_trend(values):
    """Tinh xu huong (slope) cua chuoi gia tri."""
    if len(values) < 2:
        return 0.0
    x = np.arange(len(values))
    coeffs = np.polyfit(x, values, 1)
    return float(coeffs[0])


def extract_window_features(window_data):
    """Trich xuat features tu 1 cua so 30 phut."""
    features = {}

    # Anomaly features
    anomaly_count = count_anomalies(window_data)
    features['anomaly_count'] = anomaly_count
    features['anomaly_rate'] = anomaly_count / len(window_data)

    # Temperature features
    temp = window_data['temperature'].values
    features['temp_mean'] = np.mean(temp)
    features['temp_max'] = np.max(temp)
    features['temp_std'] = np.std(temp)
    features['temp_trend'] = compute_trend(temp)

    # Humidity features
    hum = window_data['humidity'].values
    features['humidity_mean'] = np.mean(hum)
    features['humidity_min'] = np.min(hum)
    features['humidity_trend'] = compute_trend(hum)

    # Smoke features
    smk = window_data['smoke'].values
    features['smoke_mean'] = np.mean(smk)
    features['smoke_max'] = np.max(smk)
    features['smoke_std'] = np.std(smk)
    features['smoke_trend'] = compute_trend(smk)

    # CO2 features
    c = window_data['co2'].values
    features['co2_mean'] = np.mean(c)
    features['co2_max'] = np.max(c)
    features['co2_trend'] = compute_trend(c)

    # Power features
    pwr = window_data['power'].values
    features['power_mean'] = np.mean(pwr)
    features['power_max'] = np.max(pwr)
    features['power_std'] = np.std(pwr)
    features['power_trend'] = compute_trend(pwr)

    return features


print("\nDang trich xuat features tu sliding windows...")
print(f"   Window size: {WINDOW_SIZE} phut, Step: {STEP_SIZE} phut")

feature_rows = []
labels = []
start_time = time.time()

for start_idx in range(0, len(df) - WINDOW_SIZE, STEP_SIZE):
    end_idx = start_idx + WINDOW_SIZE
    window = df.iloc[start_idx:end_idx]

    # Label = risk level cao nhat trong 30 phut SAU window (du bao)
    future_start = end_idx
    future_end = min(end_idx + WINDOW_SIZE, len(df))

    if future_end <= future_start:
        continue

    future_window = df.iloc[future_start:future_end]
    label = int(future_window['risk_level'].max())

    features = extract_window_features(window)
    feature_rows.append(features)
    labels.append(label)

extraction_time = time.time() - start_time
print(f"   Trich xuat xong: {len(feature_rows)} windows trong {extraction_time:.2f}s")

# ================== BUILD DATASET ==================
X = pd.DataFrame(feature_rows)
y = np.array(labels)

FEATURE_NAMES = list(X.columns)

print(f"\nFeatures ({len(FEATURE_NAMES)}):")
for fn in FEATURE_NAMES:
    print(f"   - {fn}")

print(f"\nPhan bo labels:")
for lbl in sorted(set(y)):
    count = np.sum(y == lbl)
    print(f"   {RISK_LABELS[lbl]:8s}: {count} ({count/len(y)*100:.1f}%)")

# ================== TRAIN/TEST SPLIT ==================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\nTrain: {len(X_train)}, Test: {len(X_test)}")

# ================== TRAIN MODEL ==================
print("\nDang train Random Forest Classifier...")
train_start = time.time()

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=5,
    random_state=42,
    class_weight='balanced',
    n_jobs=-1
)
model.fit(X_train, y_train)

train_time = time.time() - train_start
print(f"Train xong trong {train_time*1000:.2f} ms")

# ================== EVALUATE ==================
print("\n" + "=" * 60)
print("KET QUA DANH GIA")
print("=" * 60)

y_pred = model.predict(X_test)

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

print(f"\n   Accuracy:  {acc:.4f}")
print(f"   Precision: {prec:.4f} (weighted)")
print(f"   Recall:    {rec:.4f} (weighted)")
print(f"   F1-Score:  {f1:.4f} (weighted)")

print(f"\nClassification Report:")
print(classification_report(
    y_test, y_pred,
    target_names=[RISK_LABELS[i] for i in sorted(RISK_LABELS.keys())],
    zero_division=0
))

print("Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(f"{'':>10s}  Pred LOW  Pred MED  Pred HIGH")
for i, row in enumerate(cm):
    print(f"   {RISK_LABELS[i]:>6s}  {row[0]:>8d}  {row[1]:>8d}  {row[2]:>9d}")

# ================== FEATURE IMPORTANCE ==================
print(f"\nTop 10 Feature Importance:")
importances = model.feature_importances_
indices = np.argsort(importances)[::-1]
for rank, idx in enumerate(indices[:10], 1):
    print(f"   {rank:2d}. {FEATURE_NAMES[idx]:<20s} {importances[idx]:.4f}")

# ================== SAVE ==================
model_data = {
    'model': model,
    'feature_names': FEATURE_NAMES,
    'risk_labels': RISK_LABELS,
    'window_size': WINDOW_SIZE,
    'metrics': {
        'accuracy': round(acc, 4),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1_score': round(f1, 4)
    }
}
joblib.dump(model_data, MODEL_PATH)
print(f"\nDa luu model tai: {MODEL_PATH}")
print("=" * 60)
