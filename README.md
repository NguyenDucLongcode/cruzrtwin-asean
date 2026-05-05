# CRUZRTWIN ASEAN - IoT Digital Twin Demo

Dự án này mô phỏng một hệ thống Digital Twin cho IoT sensor theo hướng:

- Chuẩn hóa dữ liệu theo NGSI-v2
- Đẩy dữ liệu vào FIWARE Orion Context Broker
- Phát hiện bất thường bằng AI (Isolation Forest)
- Tối ưu điện năng bằng phát hiện thiết bị idle và sinh command điều khiển smart plug

README này là bản tổng hợp để chạy nhanh toàn bộ luồng demo trong repository.

## 1. Tổng quan cấu trúc

```text
cruzrtwin-asean/
|- ai-models/
|  |- energy/
|  |  |- energy_optimizer.py
|  |  `- energy_demo.py
|  |- prediction/
|  |  |- generate_risk_data.py
|  |  |- train_risk_model.py
|  |  |- risk_predictor.py
|  |  |- risk_demo.py
|  |  |- data/risk_history.csv
|  |  |- models/
|  |  `- test/
|  `- training/
|     |- generate_sensor_data.py
|     |- train_anomaly_model.py
|     |- anomaly_detection.py
|     |- data/sensor_data.csv
|     |- models/
|     `- test/
|- data-models/
|  |- entities/
|  |- validate_entities.py
|  `- test_fiware.py
|- fiware/
|  |- docker-compose.yml
|  |- test_entities.py
|  |- create_subscription.py
|  `- postman_collection.json
|- docs/
|  |- ai-module.md
|  |- risk-prediction.md
|  |- data-models.md
|  |- fiware-module.md
|  `- matter-mapping.md
`- requirements.txt
```

## 2. Yêu cầu môi trường

- Python 3.10+
- Docker Desktop (để chạy FIWARE Orion + MongoDB)
- pip

## 3. Cài đặt nhanh

### 3.1 Tạo và kích hoạt virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Mac/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3.2 Cài dependencies

```bash
pip install -r requirements.txt
```

## 4. Chạy luồng AI end-to-end

Thứ tự đề nghị:

1. Tạo dữ liệu giả lập

```bash
python ai-models/training/generate_sensor_data.py
```

2. Train model anomaly

```bash
python ai-models/training/train_anomaly_model.py
```

3. So sánh thuật toán anomaly (benchmark nhanh)

```bash
python ai-models/training/anomaly_detection.py
```

4. Chạy bộ test training

```bash
python ai-models/training/test/run_all_tests.py
```

Lưu ý: script run_all_tests.py có bước nhấn Enter trước mỗi bài test.

5. Chạy demo energy optimization (2 scenario idle)

```bash
python ai-models/energy/energy_demo.py
```

6. Tạo dữ liệu risk prediction (T-011)

```bash
python ai-models/prediction/generate_risk_data.py
```

7. Train model dự đoán rủi ro

```bash
python ai-models/prediction/train_risk_model.py
```

8. Chạy demo risk prediction (3 scenario)

```bash
python ai-models/prediction/risk_demo.py
```

9. Chạy test risk prediction

```bash
python ai-models/prediction/test/test_risk_prediction.py
```

## 5. Data models (NGSI-v2)

Trong thư mục data-models/entities có các entity mẫu:

- TemperatureSensor
- HumiditySensor
- SmokeSensor
- AirQualitySensor
- SmartPlug

Chạy validate JSON entities:

```bash
python data-models/validate_entities.py
```

Lưu ý quan trọng: script validate đang đọc file theo working directory hiện tại.
Nếu gặp tình trạng không tìm thấy file, hãy chạy lệnh trong thư mục data-models.

Push một entity lên Orion để test nhanh:

```bash
python data-models/test_fiware.py
```

## 6. FIWARE module

### 6.1 Khởi động Orion + MongoDB

```bash
docker compose -f fiware/docker-compose.yml up -d
```

Kiểm tra Orion:

- http://localhost:1026/version

### 6.2 Test CRUD entity với script mẫu

```bash
python fiware/test_entities.py
```

Script test_entities.py đang theo flow an toàn: create, read, update, final check và không xóa entity cuối luồng.

### 6.3 Tạo subscription

```bash
python fiware/create_subscription.py
```

Mặc định webhook đang trỏ tới:

- http://host.docker.internal:8000/webhook/anomaly

Nếu service webhook của bạn dùng URL khác, cần sửa trong script create_subscription.py.

## 7. Luồng tích hợp tổng thể

```text
Sensor JSON (NGSI-v2)
-> Validate entities
-> FIWARE Orion
-> AI anomaly detection
-> Energy idle detection
-> Tạo FIWARE command để điều khiển SmartPlug
-> Risk prediction (30 phút tiếp theo)
-> Tạo RiskAlert entity -> Robot CRUZR action
```

## 8. Tài liệu chi tiết

- docs/ai-module.md
- docs/risk-prediction.md
- docs/data-models.md
- docs/fiware-module.md
- docs/matter-mapping.md

## 9. Troubleshooting nhanh

- Không kết nối được Orion: kiểm tra Docker containers mongo và orion đang chạy; kiểm tra port 1026 không bị xung đột.

- Lỗi thiếu model anomaly_model.pkl khi chạy energy: chạy trước lệnh train model:

```bash
python ai-models/training/train_anomaly_model.py
```

- Lỗi không tìm thấy file entity khi validate: chạy script validate từ đúng thư mục data-models.

## 10. Ghi chú

- Đây là repository demo học tập và trình diễn luồng tích hợp
- Dữ liệu training hiện tại là synthetic data
- Có thể mở rộng thêm API realtime, dashboard và alert pipeline khi cần
