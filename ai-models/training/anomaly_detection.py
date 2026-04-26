import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.metrics import classification_report, confusion_matrix
import time
import os

# ================== PATH ==================
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "data", "sensor_data.csv")

# Đọc dữ liệu
df = pd.read_csv(DATA_PATH)
features = ['temperature', 'humidity', 'smoke', 'co2', 'power']
X = df[features]
y_true = df['label']

# Dictionary chứa các model
models = {
    'Isolation Forest': IsolationForest(
        contamination=0.05,  # 5% dữ liệu là bất thường
        random_state=42
    ),
    'One-Class SVM': OneClassSVM(
        nu=0.05,  # 5% outlier
        kernel='rbf',
        gamma='auto'
    ),
    'Local Outlier Factor': LocalOutlierFactor(
        contamination=0.05,
        novelty=False  # LOF không support predict() với novelty=True
    )
}

print("=" * 60)
print("So sánh các thuật toán phát hiện bất thường")
print("=" * 60)

results = []

for name, model in models.items():
    print(f"\nĐang chạy: {name}")
    
    # Đo thời gian train
    start_train = time.time()
    
    if name == 'Local Outlier Factor':
        # LOF fit_predict trực tiếp
        start_pred = time.time()
        y_pred = model.fit_predict(X)
        train_time = time.time() - start_train
        pred_time = time.time() - start_pred
        # LOF trả về: 1 = inlier, -1 = outlier
        y_pred = [1 if x == 1 else 0 for x in y_pred]  # Chuyển về 0/1
    else:
        model.fit(X)
        train_time = time.time() - start_train
        
        # Đo thời gian predict
        start_pred = time.time()
        y_pred = model.predict(X)
        pred_time = time.time() - start_pred
        # Chuyển -1/1 về 0/1
        y_pred = [1 if x == -1 else 0 for x in y_pred]
    
    # Tính accuracy
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    results.append({
        'Model': name,
        'Train Time (ms)': train_time * 1000,
        'Predict Time (ms)': pred_time * 1000,
        'Total Latency (ms)': (train_time + pred_time) * 1000,
        'Accuracy': acc,
        'Precision': prec,
        'Recall': rec,
        'F1-Score': f1
    })
    
    print(f"   Train: {train_time*1000:.2f} ms")
    print(f"   Predict: {pred_time*1000:.2f} ms")
    print(f"   Accuracy: {acc:.4f}")
    print(f"   F1-Score: {f1:.4f}")

# So sánh kết quả
print("\n" + "=" * 60)
print("KẾT QUẢ SO SÁNH")
print("=" * 60)
results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

# Chọn model tốt nhất
best_model = results_df.loc[results_df['F1-Score'].idxmax()]
print("\n" + "=" * 60)
print(f"   MODEL ĐƯỢC CHỌN: {best_model['Model']}")
print(f"   - F1-Score: {best_model['F1-Score']:.4f}")
print(f"   - Latency dự kiến: {best_model['Total Latency (ms)']:.2f} ms")
print("=" * 60)