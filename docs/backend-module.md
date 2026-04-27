# Backend Module - API and Integration Guide

Module backend cung cấp REST API và WebSocket cho dashboard, đồng bộ dữ liệu từ FIWARE, và tích hợp AI để đánh giá rủi ro + tối ưu năng lượng.

---

## Mục tiêu

- Cung cấp API đọc dữ liệu sensor theo thời gian thực từ FIWARE Orion
- Tính toán risk score cho từng thiết bị và tổng quan hệ thống
- Phân tích năng lượng và đề xuất FIWARE command từ AI optimizer
- Hỗ trợ thực thi command xuống Orion với chế độ an toàn dry-run

---

## Cấu trúc thư mục

```text
backend/
|- main.py
|- config.py
|- models.py
|- api/
|  |- sensors.py
|  |- risk.py
|  |- energy.py
|  `- alerts.py
|- services/
|  |- fiware_service.py
|  |- risk_service.py
|  |- energy_service.py
|  `- websocket_manager.py
`- tests/
   `- test_api_regression.py
```

---

## Các endpoint chính

- GET / : thông tin service và danh sách endpoint
- GET /health : health check và kết nối Orion
- GET /api/sensors/ : lấy tất cả sensor
- GET /api/sensors/{device_id} : lấy 1 sensor theo id
- GET /api/risk/summary : tổng quan risk score
- GET /api/risk/{device_id} : risk score theo thiết bị
- GET /api/energy/stats : thống kê năng lượng gọn
- GET /api/energy/analysis : phân tích năng lượng chi tiết (AI + recommendation + command)
- POST /api/energy/execute : thực thi FIWARE command (mặc định dry-run)
- WS /ws : kênh WebSocket cho ping/pong và alert

---

## Hướng dẫn chạy backend

Từ thư mục root project:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Kiểm tra nhanh:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

---

## Luồng tích hợp

```text
FIMAT -> FIWARE Orion -> Backend services -> API/WebSocket -> Dashboard
                              |
                              +-> Risk service (rule + anomaly model)
                              +-> Energy service (EnergyOptimizer)
                              +-> Execute command -> Orion PATCH /entities/{id}/attrs
```

---

## Chi tiết tích hợp AI

### Risk service

- Đầu vào: dữ liệu sensor parse từ entity NGSI-v2

- Cơ chế:
  - Rule threshold (temperature, smoke, CO2, AQI)
  - AI anomaly model (Isolation Forest) nếu có model

- Fallback:
  - Nếu không load được model, hệ thống vẫn chạy theo rule-based

---

### Energy service

- Đầu vào: các SmartPlug entities từ Orion

- Cơ chế:
  - Gọi EnergyOptimizer trong ai-models/energy/energy_optimizer.py
  - Trả về recommendations và fiware_commands

- Fallback:
  - Nếu không load được optimizer/model, trả về kết quả rule-based

---

## Execute command API

Endpoint: POST /api/energy/execute

### Request mặc định (an toàn)

```json
{
  "dry_run": true
}
```

---

### Request thực thi thật

```json
{
  "dry_run": false,
  "commands": [
    {
      "command": "toggle_smart_plug",
      "device_id": "matter_smartplug_001",
      "payload": {
        "onOff": {
          "type": "Boolean",
          "value": false
        }
      }
    }
  ]
}
```

---

### Response tổng quan

- success: true/false
- source: ai-analysis | request
- dry_run: true/false
- total_commands: tổng số command
- executed: số command đã chạy
- failed: số command lỗi
- results: kết quả từng command

---

## Test tự động

Chạy regression test backend:

```bash
python -m pytest backend/tests -q
```

---

### Bao gồm các test

- Health endpoint
- Sensors list / detail / not-found
- Risk summary / detail
- Energy stats / analysis
- Energy execute (dry-run và custom command)
- WebSocket ping/pong

---

## Lưu ý vận hành

- `/api/energy/execute` nên để mặc định dry-run trong môi trường demo
- Nếu bật execute thật, cần thêm API key / authorization trước khi public
- Health check Orion sử dụng endpoint `/version` (không phải `/v2/version`)
- Khi dùng Ctrl+C để dừng service, có thể thấy exit code 1 (bình thường)

---

## Gợi ý mở rộng

- Thêm authentication cho endpoint execute
- Thêm whitelist device ID được phép điều khiển
- Lưu lịch sử command vào MongoDB để audit
- Thêm metrics và structured logging cho monitoring dashboard
