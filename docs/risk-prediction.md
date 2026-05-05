# T-011: Module Du doan Rui ro Moi truong (Risk Prediction)

Thu muc `ai-models/prediction/` chua module AI du doan rui ro moi truong
trong 30 phut tiep theo, giup he thong chuyen tu "bi dong phan ung" sang
"chu dong phong ngua".

---

## Cau truc thu muc

```text
ai-models/prediction/
├── generate_risk_data.py       # Tao du lieu time-series voi pattern rui ro
├── train_risk_model.py         # Trich xuat features + train Random Forest
├── risk_predictor.py           # Module chinh: predict + display + FIWARE alert
├── risk_demo.py                # Demo 3 scenario
├── data/
│   └── risk_history.csv        # Dataset 4320 mau (3 ngay)
├── models/
│   └── risk_model.pkl          # Model da train
└── test/
    └── test_risk_prediction.py # Bo test (23 test cases)
```

---

## Luong hoat dong

```text
Sensor Data (30 phut) → Sliding Window Features → Random Forest Classifier
  → Risk Level (LOW/MEDIUM/HIGH)
  → Console Display (chi tiet + risk bar)
  → FIWARE RiskAlert Entity → Robot CRUZR Action
```

---

## Huong dan su dung

### 1. Tao du lieu

```bash
python ai-models/prediction/generate_risk_data.py
```

Ket qua:
- Tao 4320 mau (3 ngay, moi phut 1 mau)
- 3 loai pattern rui ro: chay tiem an, ro ri CO2, thiet bi qua tai
- Phan bo: ~80% LOW, ~10% MEDIUM, ~10% HIGH

### 2. Train model

```bash
python ai-models/prediction/train_risk_model.py
```

Ket qua:
- Trich xuat 20 features tu sliding windows 30 phut
- Train Random Forest Classifier (200 trees)
- In metrics: Accuracy, Precision, Recall, F1 per class
- Luu model tai `ai-models/prediction/models/risk_model.pkl`

### 3. Chay demo

```bash
python ai-models/prediction/risk_demo.py
```

Demo 3 scenario:
1. Chay tiem an phong server → du doan HIGH
2. Ro ri CO2 tang ham → du doan HIGH
3. Hoat dong binh thuong → du doan LOW

### 4. Chay test

```bash
python ai-models/prediction/test/test_risk_prediction.py
```

---

## Features su dung (20 dac trung)

Model trich xuat tu sliding window 30 phut:

| Nhom | Features | Y nghia |
|---|---|---|
| Anomaly | anomaly_count, anomaly_rate | So/ty le bat thuong (dung model T-07) |
| Temperature | temp_mean, temp_max, temp_std, temp_trend | Thong ke + xu huong nhiet do |
| Humidity | humidity_mean, humidity_min, humidity_trend | Thong ke + xu huong do am |
| Smoke | smoke_mean, smoke_max, smoke_std, smoke_trend | Thong ke + xu huong khoi |
| CO2 | co2_mean, co2_max, co2_trend | Thong ke + xu huong CO2 |
| Power | power_mean, power_max, power_std, power_trend | Thong ke + xu huong dien |

---

## Cau hinh model

- Thuat toan: **Random Forest Classifier**
- n_estimators: 200
- max_depth: 15
- class_weight: balanced
- Window size: 30 phut
- Step size: 5 phut (khi train)

---

## Risk Levels va Robot Actions

| Risk Level | Dieu kien | Robot Action | Mo ta |
|---|---|---|---|
| LOW | Moi truong on dinh | MONITOR | Robot tiep tuc giam sat binh thuong |
| MEDIUM | Co dau hieu bat thuong | INSPECT_AREA | Robot di chuyen den khu vuc kiem tra |
| HIGH | Rui ro cao | PATROL_AND_ANNOUNCE | Robot tuan tra + phat canh bao giong noi |

---

## FIWARE Alert Entity (NGSI-v2)

Moi du doan tao ra 1 entity `RiskAlert` de gui len FIWARE Orion:

```json
{
  "id": "urn:ngsi-ld:RiskAlert:alert_20260505120000",
  "type": "RiskAlert",
  "riskLevel": { "type": "Text", "value": "HIGH" },
  "riskScore": { "type": "Number", "value": 0.87 },
  "predictedFor": { "type": "DateTime", "value": "2026-05-05T12:30:00" },
  "probabilities": { "type": "StructuredValue", "value": {"LOW": 0.05, "MEDIUM": 0.08, "HIGH": 0.87} },
  "topFactors": { "type": "StructuredValue", "value": [...] },
  "robotAction": { "type": "Text", "value": "PATROL_AND_ANNOUNCE" },
  "message": { "type": "Text", "value": "CANH BAO KHAN CAP: ..." },
  "sensorSnapshot": { "type": "StructuredValue", "value": {...} },
  "source": { "type": "Text", "value": "T-011_Risk_Predictor" }
}
```

---

## Tich hop he thong

```text
FIWARE Orion → Sensor Data (30 phut)
  → T-011 Risk Predictor
  → RiskAlert Entity → POST len Orion
  → Robot CRUZR doc alert → Thuc hien action (MONITOR/INSPECT/PATROL)
```

---

## Ghi chu

- Du lieu hien tai la synthetic (gia lap)
- Model co the retrain khi co du lieu that tu sensor
- Module tich hop voi model T-07 (anomaly detection) de dem anomaly trong window
- F1-Score hien tai: ~87% (weighted), du tin cay cho demo
