# Backend Module - API and Integration Guide

Module backend cung cap REST API va WebSocket cho dashboard, dong bo du lieu tu FIWARE Orion, xu ly alert tu webhook, va tich hop AI cho risk + energy.

---

## Muc tieu

- Cung cap API doc du lieu sensor theo thoi gian thuc tu FIWARE Orion
- Tinh risk score cho tung thiet bi va tong quan he thong
- Phan tich nang luong va de xuat FIWARE command tu AI optimizer
- Ho tro thuc thi command xuong Orion voi che do an toan dry-run
- Nhan webhook anomaly tu FIWARE, broadcast qua WebSocket va forward sang robot API

---

## Cau truc thu muc

```text
backend/
|- main.py
|- config.py
|- models.py
|- api/
|  |- sensors.py
|  |- risk.py
|  |- energy.py
|  |- webhook.py
|  |- health.py
|  `- alerts.py
|- services/
|  |- fiware_service.py
|  |- risk_service.py
|  |- energy_service.py
|  |- alert_service.py
|  `- websocket_manager.py
|- websocket/
|  `- ws_handler.py
`- tests/
   `- test_api_regression.py
```

---

## Router dang include trong app

Trong `main.py`, backend include cac router sau:

- `sensors.router` (prefix `/api/sensors`)
- `risk.router` (prefix `/api/risk`)
- `energy.router` (prefix `/api/energy`)
- `webhook.router` (prefix `/api/webhook`)
- `health.router` (route `/health`)
- `alerts.router` (prefix `/api/alerts`)

---

## Cac endpoint chinh

- GET `/` : thong tin service va danh sach endpoint co ban
- GET `/health` : health check service + ket noi Orion (`/version`)
- GET `/api/sensors/` : lay tat ca sensor
- GET `/api/sensors/{device_id}` : lay 1 sensor theo id
- GET `/api/risk/summary` : tong quan risk score toan he thong
- GET `/api/risk/{device_id}` : risk score theo thiet bi
- GET `/api/energy/stats` : thong ke nang luong tong hop
- GET `/api/energy/analysis` : phan tich nang luong chi tiet (AI/rule-based + recommendation + fiware_commands)
- POST `/api/energy/execute` : thuc thi FIWARE command (mac dinh dry-run)
- POST `/api/webhook/anomaly` : nhận anomaly alert từ FIWARE subscription
- POST `/api/webhook/livingroom` : nhận notification living-room (motion + smartplug) — luồng năng lượng và motion sensor sẽ gửi về đây
- GET `/api/alerts/` : lay danh sach alert gan nhat cho dashboard
- GET `/api/alerts/latest` : lay alert moi nhat
- WS `/ws` : kenh WebSocket cho connection message, ping/pong va alert

---

## Huong dan chay backend

Tu thu muc root project:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Kiem tra nhanh:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

---

## Luong tich hop

```text
FIMAT -> FIWARE Orion -> Backend services -> API/WebSocket -> Dashboard
                              |
                              +-> Risk service (rule + anomaly model neu co)
                              +-> Energy service (EnergyOptimizer neu load duoc)
                              +-> Execute command -> Orion PATCH /entities/{id}/attrs

FIWARE Subscription -> POST /api/webhook/anomaly -> alert_service
                                            |
                                            +-> WebSocket broadcast
                                            +-> Forward robot API (http://127.0.0.1:8001/api/robot/alert)
```

---

## Chi tiet tich hop AI

### Risk service

- Dau vao: du lieu sensor parse tu entity NGSI-v2
- Co che:
  - Rule threshold (temperature, smoke, CO2, AQI)
  - Thu model anomaly tu file `ai-models/training/models/anomaly_model.pkl`
  - Neu model predict bat thuong (`-1`) thi cong them risk
- Fallback:
  - Neu khong load duoc model, van tinh theo rule-based va them ly do `AI model chua san sang, dang dung rule-based`

### Energy service

- Dau vao: cac `SmartPlug` entities tu Orion
- Neu co QuantumLeap: lay them lich su `power` (time-series) theo `lastN`
- Co che:
  - Dynamic load `EnergyOptimizer` tu `ai-models/energy/energy_optimizer.py`
  - Uu tien feed du lieu lich su vao optimizer de detect idle on dinh hon
  - Neu load duoc optimizer: tra ve `mode: ai`, recommendations, fiware_commands
- Fallback:
  - Neu khong co time-series/khong load duoc optimizer/model: tra ve `mode: rule-based` + recommendation don gian

---

## Execute command API

Endpoint: POST `/api/energy/execute`

### Request mac dinh (an toan)

```json
{
  "dry_run": true
}
```

Khi khong truyen `commands`, backend tu dong lay danh sach command tu `/api/energy/analysis` (source = `ai-analysis`).

### Request thuc thi that

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

### Response tong quan

- `success`: true/false
- `source`: `ai-analysis` | `request`
- `dry_run`: true/false
- `total_commands`: tong so command
- `executed`: so command thanh cong
- `failed`: so command that bai
- `results`: ket qua tung command

Luu y: hien backend chi ho tro command `toggle_smart_plug`; payload phai chua `payload.onOff.value`.

---

## Webhook anomaly & livingroom API

Endpoints:

- POST `/api/webhook/anomaly` — nhận anomaly alerts từ các subscription chung
- POST `/api/webhook/livingroom` — nhận notification chuyên dụng cho phòng khách (motion sensor + smartplug)

Input: payload notification từ FIWARE subscription (`data` là danh sách entity)

Xử lý chung:

- Parse thành danh sách alert
- Broadcast qua WebSocket manager
- Forward alert sang robot API (được debounce ở backend: cùng một alert sẽ không được forward nhiều lần trong vòng 30s)

Response:

- `status`, `message`, `processed`, `forwarded`

---

## Test tu dong

Chay regression test backend:

```bash
python -m pytest backend/tests -q
```

### Bao gom cac test hien co

- Health endpoint (`/health`)
- Sensors list / detail / not-found
- Risk summary / detail
- Energy stats / analysis
- Energy execute (dry-run va custom command)
- WebSocket ping/pong

Luu y: file regression test hien chua cover endpoint webhook.

---

## Luu y van hanh

- `/api/energy/execute` nen de mac dinh `dry_run=true` trong moi truong demo
- Neu bat execute that, nen bo sung auth/API key truoc khi expose
- Health check Orion dung endpoint `/version` (khong phai `/v2/version`)
- Alert history hien luu in-memory (mat khi restart service)

---

## Goi y mo rong

- Them authentication cho endpoint execute va webhook
- Them whitelist device ID duoc phep dieu khien
- Luu lich su command vao database de audit
- Bo sung test regression cho `/api/webhook/anomaly`
- Them metrics va structured logging cho monitoring dashboard
