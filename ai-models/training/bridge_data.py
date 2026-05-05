import pandas as pd
import numpy as np
import os

# Paths
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "data", "sensor_data.csv")

if not os.path.exists(DATA_PATH):
    print(f"Error: {DATA_PATH} not found.")
    exit(1)

print(f"Reading data from {DATA_PATH}")
df = pd.read_csv(DATA_PATH)

# Adapt columns
# cruzrtwin-asean expects: timestamp, temperature, humidity, smoke, co2, power, label
# CruzrTwin-Tan has: timestamp, temperature, humidity, co2, is_anomaly, anomaly_type

# Rename is_anomaly to label
if 'is_anomaly' in df.columns:
    df.rename(columns={'is_anomaly': 'label'}, inplace=True)

# Add smoke
if 'smoke' not in df.columns:
    print("Adding synthetic 'smoke' column...")
    # Normal: low smoke (30-60), Fire risk: high smoke (200-500)
    df['smoke'] = np.random.uniform(30, 60, len(df))
    if 'anomaly_type' in df.columns:
        df.loc[df['anomaly_type'] == 'fire_risk', 'smoke'] = np.random.uniform(200, 500, len(df[df['anomaly_type'] == 'fire_risk']))

# Add power
if 'power' not in df.columns:
    print("Adding synthetic 'power' column...")
    # Normal power usage
    df['power'] = np.random.uniform(20, 100, len(df))

# Ensure columns are in the right order for consistency (optional)
expected_cols = ['timestamp', 'temperature', 'humidity', 'smoke', 'co2', 'power', 'label']
# Check if all exist
for col in expected_cols:
    if col not in df.columns:
        print(f"Warning: missing {col}, adding as 0")
        df[col] = 0

df_final = df[expected_cols]

# Save back
df_final.to_csv(DATA_PATH, index=False)
print(f"Successfully adapted data and saved to {DATA_PATH}")
print(df_final.head())
