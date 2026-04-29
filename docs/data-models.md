# 🌐 Data Models & FIWARE Integration

Thư mục `data-models/` chứa các định nghĩa dữ liệu sensor và cách tương tác với FIWARE Orion Context Broker.

---

## 📁 Cấu trúc thư mục

```
data-models/
│── entities/
│   ├── TemperatureSensor.json
│   ├── HumiditySensor.json
│   ├── SmokeSensor.json
│   ├── AirQualitySensor.json
│   └── SmartPlug.json
│
│── validate_entities.py   # Validate JSON theo NGSI-v2
│── test_fiware.py       # Gửi dữ liệu lên FIWARE Orion
```

---

## 🎯 Mục tiêu

- Chuẩn hóa dữ liệu sensor theo **NGSI-v2**
- Gửi dữ liệu lên **FIWARE Orion Context Broker**
- Làm nguồn input cho AI module

---

## 📊 Định dạng dữ liệu (NGSI-v2)

Mỗi sensor được biểu diễn dưới dạng JSON:

```json
{
  "id": "urn:ngsi-ld:TemperatureSensor:sensor_001",
  "type": "TemperatureSensor",
  "temperature": {
    "type": "Number",
    "value": 25.5
  }
}
```

---

## 1. Validate dữ liệu

Chạy:

```bash
python data-models/validate_entities.py
```

👉 Kiểm tra:

- Có `id`, `type`
- Đúng format NGSI
- TimeInstant hợp lệ

---

## 🚀 2. Gửi dữ liệu lên FIWARE

Chạy:

```bash
python data-models/test_fiware.py
```

👉 Script sẽ:

- Đọc tất cả file trong `entities/`
- Gửi từng entity lên Orion

---

## 🔍 3. Kiểm tra dữ liệu

Mở trình duyệt:

```
http://localhost:1026/version
```

👉 Nếu thấy JSON → Orion đang chạy

---

Hoặc GET entity:

```
http://localhost:1026/v2/entities
```

---

## 🔄 Luồng dữ liệu

```
JSON Sensor → Validate → FIWARE Orion → MongoDB → AI Module
```

---

## 📌 Ghi chú

- Orion chạy tại: `http://localhost:1026`
- MongoDB chạy port: `27017`
- Dữ liệu hiện tại là giả lập (demo)

---

## 🔗 Liên kết với AI Module

Dữ liệu từ FIWARE sẽ được dùng cho:

```
FIWARE → AI (Isolation Forest) → Detect Anomaly
```

---

## 🚀 Mở rộng

- Kết nối thiết bị IoT thật
- Streaming realtime (MQTT)
- Dashboard visualization
- Alert system

---

## 🔔 Ghi chú cho Living Room

- Các entity `SmartPlug` và motion sensor (ví dụ `MotionPIRSensor.json`) thường được dùng cho luồng "living room".
- Để nhận notification từ Orion cho phòng khách, tạo subscription (xem `fiware/create_subscription.py`). Nên chạy script trong `.venv`:

```powershell
.\.venv\Scripts\Activate.ps1
python fiware/create_subscription.py
```

Subscription cho phòng khách mặc định sẽ gửi về `/api/webhook/livingroom` ở backend.
