import pandas as pd
import joblib
import os

print("\n" + "=" * 50)
print("TEST 3: Kiểm tra với dữ liệu thật từ CSV")
print("=" * 50)

# BASE DIR CHUẨN (ai-models/)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# PATH CSV
CSV_PATH = os.path.join(BASE_DIR, "data","sensor_data.csv")
MODEL_PATH = os.path.join(BASE_DIR,"models", "anomaly_model.pkl")

# Load data
df = pd.read_csv(CSV_PATH)

# Load model
model = joblib.load(MODEL_PATH)
print("Model loaded successfully")

# Features
features = ['temperature', 'humidity', 'smoke', 'co2', 'power']

X_test = df[features].head(10)
y_true = df['label'].head(10)

print("\nDự đoán 10 mẫu đầu tiên:")
print("-" * 80)

for i in range(len(X_test)):
    data = X_test.iloc[i].values

    pred = model.predict([data])[0]
    pred_label = 1 if pred == -1 else 0

    true_label = y_true.iloc[i]

    result = "ĐÚNG" if pred_label == true_label else "SAI"
    status = "BẤT THƯỜNG" if pred_label == 1 else "BÌNH THƯỜNG"

    print(
        f"Mẫu {i+1}: {status} | "
        f"Thực tế: {'Bất thường' if true_label==1 else 'Bình thường'} | {result}"
    )