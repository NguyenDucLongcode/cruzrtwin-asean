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
|- fimat/
|  |- config.py
|  |- matter_simulator.py
|  |- fiware_publisher.py
|  `- fimat_service.py
|- backend/
|  |- main.py
|  |- config.py
|  |- models.py
|  |- api/
|  `- services/
|- docs/
|  |- ai-module.md
|  |- backend-module.md
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
- http://localhost:8668/version (QuantumLeap)

### 6.2 Test CRUD entity với script mẫu

```bash
python fiware/test/test_entities.py
```

Script test_entities.py đang theo flow an toàn: create, read, update, final check và không xóa entity cuối luồng.

### 6.3 Tạo subscription

```bash
python fiware/create_subscription.py

```

- 'curl -s http://localhost:1026/v2/subscriptions'
  Api mặc định API mặc định của FIWARE Orion.

---

---

### Taọ thêm subscription de luu time-series vao QuantumLeap/CrateDB:

---

- `curl "http://localhost:8668/v2/entities/[id]/attrs/power?lastN=20"`

Đây là API của QuantumLeap , dùng để lấy lịch sử dữ liệu đã được lưu trong CrateDB.

```bash
python fiware/create_timeseries_subscription.py
```

Mặc định webhook đang trỏ tới:

- http://host.docker.internal:8000/webhook/anomaly

Nếu service webhook của bạn dùng URL khác, cần sửa trong script create_subscription.py.

### 6.4 Chạy FIMAT (Matter -> FIWARE realtime)

```bash
python fimat/fimat_service.py
```

Service sẽ:

- Tạo 5 entity `matter_*` (Temperature, Humidity, Smoke, AirQuality, SmartPlug)
- Đồng bộ dữ liệu realtime theo interval trong `fimat/config.py`
- Cập nhật các field mở rộng đã map theo NGSI-v2:
  - AirQuality: `pm25`, `pm10`, `co2`, `tvoc`, `aqi`
  - SmartPlug: `power`, `voltage`, `current`, `energyToday`, `onOff`

Kiểm tra nhanh entities sau khi chạy:

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:1026/v2/entities?limit=1000&options=keyValues"
```

## 7. Backend API (Dashboard/API layer)

Chạy backend:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Kiểm tra nhanh:

- `GET http://localhost:8000/health`
- `GET http://localhost:8000/api/sensors/`
- `GET http://localhost:8000/api/risk/summary`
- `GET http://localhost:8000/api/energy/stats`
- `GET http://localhost:8000/api/energy/analysis`
- `POST http://localhost:8000/api/energy/execute`
- `WS  ws://localhost:8000/ws`
- Mở browser tại: `http://localhost:8000/docs` để xem Swagger UI(dành cho dân thích test api bằng giao diện)

Liên kết hệ thống trong backend:

- `Sensors API` đọc dữ liệu trực tiếp từ FIWARE Orion
- `Risk API` kết hợp rule thresholds + model Isolation Forest (nếu model sẵn sàng)
- `Energy API` gọi AI Energy Optimizer để trả khuyến nghị + FIWARE command dự kiến
- `Energy Execute API` thực thi command xuống FIWARE Orion (mặc định dry-run để an toàn)
- Nếu chưa load được model AI, backend tự fallback sang rule-based để không ngắt dịch vụ

Ví dụ thực thi command ở chế độ an toàn (không ghi xuống Orion):

```bash
curl -X POST http://localhost:8000/api/energy/execute \
  -H "Content-Type: application/json" \
  -d '{"dry_run": true}'
```

Ví dụ thực thi thật command tự truyền vào request:

```bash
curl -X POST http://localhost:8000/api/energy/execute \
  -H "Content-Type: application/json" \
  -d '{
    "dry_run": false,
    "commands": [
      {
        "command": "toggle_smart_plug",
        "device_id": "matter_smartplug_001",
        "payload": {"onOff": {"type": "Boolean", "value": false}}
      }
    ]
  }'
```

Chạy regression test cho backend:

```bash
python -m pytest backend/tests -q
```

## 8. Luồng tích hợp tổng thể

```text
Sensor JSON (NGSI-v2)
-> Validate entities
-> FIWARE Orion
-> FIMAT realtime sync (Matter simulation)
-> Backend API + WebSocket
-> AI anomaly detection
-> Energy idle detection
-> Tạo FIWARE command để điều khiển SmartPlug
```

## 9. Tài liệu chi tiết

- docs/ai-module.md
- docs/backend-module.md
- docs/data-models.md
- docs/fiware-module.md
- docs/matter-mapping.md
- **docs/validation-report.md** ← Kiểm tra cho Subscription + Production Readiness

## 10. Validation & Testing Status

### ✅ Latest Validation (2026-04-27)

**Regression Tests:** 9/9 passing ✅

```bash
✅ Sensors API (CRUD, extended fields)
✅ Risk API (summary + per-device scoring)
✅ Energy API (stats, analysis, execution)
✅ Webhook API (subscription integration)
✅ WebSocket (real-time alerts)
✅ Health Check (Orion connectivity)
```

**FIWARE Subscriptions:** 3/3 active ✅

- Temperature > 35°C → Webhook notifications
- Smoke > 300ppm → Webhook notifications
- CO2 > 1000ppm → Webhook notifications
- Webhook endpoint responding correctly

**System Integration:** Full end-to-end ✅

- FIMAT → Orion → Backend API → AI Models → Command Execution

**For Production Deployment:** See docs/validation-report.md

- Current readiness: 65/100
- Recommended hardening: Authentication, HTTPS, Rate Limiting, Logging
- Estimated time to production-ready: 2-3 hours

## 11. Troubleshooting nhanh

- Không kết nối được Orion: kiểm tra Docker containers mongo và orion đang chạy; kiểm tra port 1026 không bị xung đột.

- Lỗi thiếu model anomaly_model.pkl khi chạy energy: chạy trước lệnh train model:

```bash
python ai-models/training/train_anomaly_model.py
```

- Lỗi không tìm thấy file entity khi validate: chạy script validate từ đúng thư mục data-models.

- `python fimat/fimat_service.py` trả `exit code 1` khi dừng: đây là dừng bằng Ctrl+C, không phải lỗi logic.

- `pip` lỗi launcher sau khi đổi tên thư mục project: dùng `python -m pip ...` hoặc cài lại pip trong `.venv`.

## 12. Ghi chú

- Đây là repository demo học tập và trình diễn luồng tích hợp
- Dữ liệu training hiện tại là synthetic data
- Có thể mở rộng thêm API realtime, dashboard và alert pipeline khi cần
