# T-014, T-015, T-016: Unified Backend REST API

Thư mục `backend/` chứa hệ thống API (viết bằng FastAPI) đóng vai trò trung gian kết nối FIWARE Context Broker, AI Modules với Dashboard (Frontend) và Robot CRUZR.

---

## 📁 Cấu trúc thư mục

```text
backend/
├── main.py              # File chạy chính của FastAPI (CORS, Router mounting)
├── routers/
│   ├── dashboard.py     # T-015: API lấy dữ liệu Sensor, Alert, Energy từ Orion
│   ├── robot.py         # T-014: API mô phỏng điều khiển Robot và IoT Relay
│   └── webhook.py       # T-016: Webhook nhận thông báo từ Orion & WebSocket push
```

---

## 🚀 Khởi chạy Backend

Yêu cầu môi trường đã cài các thư viện trong `requirements.txt`:
```bash
# Cài đặt thư viện nếu chưa có
pip install fastapi uvicorn websockets httpx

# Chạy server ở chế độ reload (cổng 8000)
uvicorn backend.main:app --reload --port 8000
```

> **Swagger UI (Tài liệu API tự động):** 
> Sau khi chạy, mở trình duyệt vào [http://localhost:8000/docs](http://localhost:8000/docs) để xem và test các endpoint trực tiếp.

---

## 🔗 Các nhóm API Endpoints

### 1. Dashboard API (T-015)
Lấy dữ liệu thời gian thực từ FIWARE Orion Context Broker.

| Endpoint | Method | Chức năng |
|---|---|---|
| `/api/dashboard/sensors` | `GET` | Lấy dữ liệu tất cả các sensor (Nhiệt độ, Độ ẩm, Khói, Chất lượng không khí). |
| `/api/dashboard/energy` | `GET` | Lấy thông tin tiêu thụ điện năng từ `SmartPlug`. |
| `/api/dashboard/alerts` | `GET` | Lấy danh sách cảnh báo (RiskAlert) gần nhất. |

### 2. Cruzr Robot & Matter IoT API (T-014)
Các API này giả lập điều khiển Robot CRUZR và ra lệnh cho các thiết bị IoT thông qua Relay.

| Endpoint | Method | Chức năng | Body Payload |
|---|---|---|---|
| `/api/robot/navigate` | `POST` | Ra lệnh Robot di chuyển. | `{"target_zone": "Room A"}` |
| `/api/robot/announce` | `POST` | Ra lệnh Robot phát cảnh báo giọng nói (TTS). | `{"message": "Fire risk detected!"}` |
| `/api/robot/matter/control` | `POST` | Relay bật/tắt thiết bị SmartPlug. | `{"device_id": "plug_001", "command": "onOff", "value": false}` |

### 3. Webhook & WebSocket (T-016)
Nhận và phân phối cảnh báo realtime.

| Endpoint | Method/Type | Chức năng |
|---|---|---|
| `/webhook/fiware` | `POST` | Nhận HTTP Notification từ FIWARE Subscription. |
| `/ws/alerts` | `WebSocket` | Cung cấp luồng dữ liệu realtime cho Dashboard khi có Alert mới. |

---

## ⚙️ Luồng hoạt động của Cảnh báo (Alert Flow)

1. **AI/Rule Engine** tạo entity `RiskAlert` hoặc `Anomaly` trên **FIWARE Orion**.
2. **Orion** trigger Subscription (tạo bởi `fiware/create_subscription.py`).
3. **Orion** gửi một HTTP POST request chứa dữ liệu Alert tới **Backend Webhook** (`/webhook/fiware`).
4. **Backend** nhận dữ liệu, xử lý và push message qua **WebSocket** (`/ws/alerts`).
5. **Dashboard** (đang kết nối WebSocket) nhận message và hiển thị popup cảnh báo.
6. **Dashboard** (hoặc AI Rule) có thể gọi tiếp `/api/robot/navigate` để ra lệnh Robot đi kiểm tra.

---

## 📌 Ghi chú
- Backend tự động kết nối với Orion ở địa chỉ mặc định `http://localhost:1026/v2`.
- Nếu triển khai qua Docker sau này, có thể thay đổi bằng biến môi trường `ORION_URL`.
- Hiện tại Robot được chạy ở chế độ **Giả lập (Simulated)**: Server chỉ in log và trả về `{"status": "success"}` thay vì gọi SDK Robot thật.
