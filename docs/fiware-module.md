# 📡 FIWARE Module - Orion Integration

Module `fiware/` dùng để kết nối, kiểm tra và thao tác dữ liệu với FIWARE Orion Context Broker theo chuẩn NGSI-v2.

---

## 📁 Cấu trúc thư mục

```text
fiware/
├── docker-compose.yml        # Chạy Orion + MongoDB + QuantumLeap + CrateDB
├── test_entities.py          # Test luồng CRUD entity an toàn
├── create_subscription.py    # Tạo subscription nhận cảnh báo bất thường
├── create_timeseries_subscription.py  # Tạo subscription đẩy dữ liệu sang QuantumLeap
└── postman_collection.json   # Bộ request test nhanh bằng Postman
```

---

## 🎯 Mục tiêu

- Khởi chạy Orion Context Broker, MongoDB, QuantumLeap, CrateDB cục bộ
- Thực hiện CRUD trên entity NGSI-v2
- Tạo subscription để đẩy notification ra webhook
- Lưu lịch sử time-series để phục vụ analytics/AI
- Làm cầu nối dữ liệu cho AI module

---

## 🚀 1. Khởi động FIWARE

Chạy tại thư mục project:

```bash
docker compose -f fiware/docker-compose.yml up -d
```

Kiểm tra Orion đã chạy:

```text
http://localhost:1026/version
```

Kiem tra QuantumLeap:

```text
http://localhost:8668/version
```

---

## 🧪 2. Test CRUD entity

Script:

```bash
python fiware/test_entities.py
```

Script sẽ chạy theo thứ tự:

1. CREATE entity `TemperatureSensor`
2. READ entity và in giá trị temperature
3. UPDATE temperature
4. FINAL CHECK để xác nhận entity còn tồn tại

Ghi chú:

- Script dùng file mẫu tại `data-models/entities/TemperatureSensor.json`
- Script hiện là luồng an toàn, không xóa entity ở cuối để giữ dữ liệu trong Orion

---

## 🔔 3. Tạo subscription cảnh báo

Script:

```bash
python fiware/create_subscription.py
```

Mặc định subscription:

- Theo dõi entity type `TemperatureSensor`
- Theo dõi thuộc tính `temperature`
- Gửi notification đến webhook:

```text
http://host.docker.internal:8000/api/webhook/anomaly
```

- `throttling = 5` giây

---

## 🕒 4. Tạo subscription lưu Time-Series

Script:

```bash
python fiware/create_timeseries_subscription.py
```

Subscription nay se forward thay doi entity tu Orion sang QuantumLeap (`http://quantumleap:8668/v2/notify`), sau do luu vao CrateDB.

Kiem tra nhanh lich su (vi du attr `power`):

```text
http://localhost:8668/v2/entities/urn:ngsi-ld:SmartPlug:plug_001/attrs/power?lastN=20
```

## 🔄 5. Tích hợp FIMAT (Matter -> FIWARE realtime)

Script:

```bash
python fimat/fimat_service.py
```

Service FIMAT sẽ thực hiện:

- `NodeAdded`: tự đăng ký entity `matter_*` lên Orion
- `AttributeUpdated`: đồng bộ dữ liệu cảm biến theo thời gian thực
- Tuân theo interval từng thiết bị trong `fimat/config.py`

Các field mở rộng đã được đồng bộ:

- `AirQualitySensor`: `pm25`, `pm10`, `co2`, `tvoc`, `aqi`
- `SmartPlug`: `power`, `voltage`, `current`, `energyToday`, `onOff`

Kiểm tra nhanh sau khi chạy:

```powershell
$entities = Invoke-RestMethod -Method Get -Uri "http://localhost:1026/v2/entities?limit=1000&options=keyValues"
$entities | Where-Object { $_.id -like "matter_*" } | Select-Object id,type
```

Lưu ý: dừng bằng `Ctrl+C` có thể hiện `exit code 1`, đây là hành vi dừng tiến trình bình thường.

---

## 🔗 Endpoints quan trọng

- Orion base URL: `http://localhost:1026/v2`
- Lấy danh sách entity: `GET /entities`
- Lấy chi tiết entity: `GET /entities/{entityId}`
- Tạo entity: `POST /entities`
- Cập nhật attrs: `PATCH /entities/{entityId}/attrs`
- Xóa entity: `DELETE /entities/{entityId}`
- Tạo subscription: `POST /subscriptions`
- Xem subscriptions: `GET /subscriptions`
- QuantumLeap lịch sử attr: `GET http://localhost:8668/v2/entities/{entityId}/attrs/{attrName}?lastN=20`

---

## 🔄 Luồng tích hợp hệ thống

```text
data-models (JSON NGSI-v2)
→ FIWARE Orion
→ FIMAT realtime sync (Matter simulation)
→ AI Module (Anomaly + Energy)
→ Notification/API/UI
```

---

## 📌 Troubleshooting nhanh

- Lỗi không kết nối Orion:
  - Kiểm tra container `orion` và `mongo` đang chạy
  - Kiểm tra đúng cổng `1026`
- Lỗi không tìm thấy file entity JSON:
  - Kiểm tra file có trong `data-models/entities/`
- Lỗi tạo subscription webhook:
  - Kiểm tra service webhook chạy ở cổng `8000`
  - Nếu chạy ngoài Docker, đổi URL nhận notification cho phù hợp

---

## 🚀 Mở rộng

- Thêm script replay dữ liệu sensor theo thời gian thực
- Bổ sung retry/backoff khi Orion timeout
- Tách cấu hình URL/port qua biến môi trường
- Đồng bộ rule subscription với AI thresholds
