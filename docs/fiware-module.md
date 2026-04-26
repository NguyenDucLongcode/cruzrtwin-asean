# 📡 FIWARE Module - Orion Integration

Module `fiware/` dùng để kết nối, kiểm tra và thao tác dữ liệu với FIWARE Orion Context Broker theo chuẩn NGSI-v2.

---

## 📁 Cấu trúc thư mục

```text
fiware/
├── docker-compose.yml        # Chạy Orion + MongoDB
├── test_entities.py          # Test luồng CRUD entity an toàn
├── create_subscription.py    # Tạo subscription nhận cảnh báo bất thường
└── postman_collection.json   # Bộ request test nhanh bằng Postman
```

---

## 🎯 Mục tiêu

- Khởi chạy Orion Context Broker và MongoDB cục bộ
- Thực hiện CRUD trên entity NGSI-v2
- Tạo subscription để đẩy notification ra webhook
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
http://host.docker.internal:8000/webhook/anomaly
```

- `throttling = 5` giây

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

---

## 🔄 Luồng tích hợp hệ thống

```text
data-models (JSON NGSI-v2)
→ FIWARE Orion
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
