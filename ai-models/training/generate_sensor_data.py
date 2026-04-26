import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)

# ================== PATH ==================
# Lấy đúng thư mục chứa file .py (ai-modules)
BASE_DIR = os.path.dirname(__file__)
OUTPUT_FILE = os.path.join(BASE_DIR, "data","sensor_data.csv")

# ================== DATA NORMAL ==================
n_normal = 1000 #Số lượng mẫu bình thường
timestamps = [datetime.now() - timedelta(minutes=i) for i in range(n_normal)]

data = {
    'timestamp': timestamps,
    'temperature': np.random.normal(25, 2, n_normal),
    'humidity': np.random.normal(60, 5, n_normal),
    'smoke': np.random.normal(50, 10, n_normal),
    'co2': np.random.normal(400, 30, n_normal),
    'power': np.random.normal(50, 15, n_normal)
}

# ================== DATA ANOMALY ==================
n_anomaly = 50 #Số lượng mẫu bất thường

anomaly_data = {
    'timestamp': [datetime.now() - timedelta(minutes=i) for i in range(n_anomaly)],
    'temperature': np.random.uniform(40, 50, n_anomaly),
    'humidity': np.random.uniform(10, 20, n_anomaly),
    'smoke': np.random.uniform(300, 500, n_anomaly),
    'co2': np.random.uniform(800, 1200, n_anomaly),
    'power': np.random.uniform(5, 10, n_anomaly)
}

# ================== MERGE ==================
# Tạo DataFrame và gán label: 0 = normal, 1 = anomaly để dễ dàng đánh giá sau này
df_normal = pd.DataFrame(data)
df_anomaly = pd.DataFrame(anomaly_data)

df = pd.concat([df_normal, df_anomaly], ignore_index=True)

# Label: 0 = normal, 1 = anomaly
df['label'] = [0] * n_normal + [1] * n_anomaly

# ================== SAVE ==================
# Lưu dữ liệu ra file CSV
df.to_csv(OUTPUT_FILE, index=False)

# ================== LOG ==================
print("Đã tạo file:", OUTPUT_FILE)
print("Tổng số mẫu:", len(df))
print(df[['temperature', 'humidity', 'smoke', 'co2', 'power', 'label']].head())