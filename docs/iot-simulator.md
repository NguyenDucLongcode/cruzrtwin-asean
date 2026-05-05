# IoT Simulator — FIWARE IoT Agent JSON

Module gia lap thiet bi IoT gui du lieu qua FIWARE IoT Agent JSON,
dung kien truc production chuan: Device -> IoT Agent -> Orion Context Broker.

---

## Kien truc

```text
Python IoT Simulator
  |
  | HTTP POST (port 7896)
  v
IoT Agent JSON (fiware/iotagent-json)
  |
  | NGSI-v2 auto-mapping
  v
FIWARE Orion Context Broker (port 1026)
  |
  v
AI Modules (Anomaly Detection, Risk Prediction, Energy Optimization)
```

---

## Cau truc file

```text
fiware/
├── docker-compose.yml        # Orion + MongoDB + IoT Agent JSON
├── provision_devices.py      # Dang ky 5 loai thiet bi
├── iot_simulator.py          # Simulator realtime (chay lien tuc)
├── iot_simulator_demo.py     # Demo 3 scenario
├── test_entities.py          # Test CRUD entity (da co)
├── create_subscription.py    # Tao subscription (da co)
└── postman_collection.json   # Postman test (da co)
```

---

## Huong dan su dung

### 1. Khoi dong FIWARE stack

```bash
docker compose -f fiware/docker-compose.yml up -d
```

Kiem tra 3 container dang chay:
- mongo (port 27017)
- orion (port 1026)
- iot-agent (port 4041 + 7896)

```bash
docker ps
```

### 2. Dang ky thiet bi

```bash
python fiware/provision_devices.py
```

Script se:
- Kiem tra ket noi Orion + IoT Agent
- Tao service group (API key: cruzrtwin2026)
- Dang ky 5 thiet bi IoT
- Xac nhan tren Orion

### 3. Chay simulator

#### Mode binh thuong (chay lien tuc)
```bash
python fiware/iot_simulator.py
```

#### Mode co inject anomaly
```bash
python fiware/iot_simulator.py --mode anomaly
```

#### Thay doi interval (mac dinh 5 giay)
```bash
python fiware/iot_simulator.py --interval 3
```

#### Demo 3 scenario (tu dong)
```bash
python fiware/iot_simulator_demo.py
```

---

## Thiet bi duoc gia lap

| Device ID | Entity Type | Attribute Mapping | Vi tri |
|---|---|---|---|
| temp_sensor_001 | TemperatureSensor | t->temperature, bat->battery | Room A |
| hum_sensor_001 | HumiditySensor | h->humidity, bat->battery | Room A |
| smoke_sensor_001 | SmokeSensor | s->smokeLevel, bat->battery | Room A |
| air_sensor_001 | AirQualitySensor | co2->co2, pm25->pm25, tvoc->tvoc | Room B |
| plug_001 | SmartPlug | p->power, v->voltage, c->current, on->onOff | Room A |

---

## IoT Agent JSON — Ports

| Port | Chuc nang | Su dung |
|---|---|---|
| 4041 | North Port (Admin) | Provision devices, query registered devices |
| 7896 | South Port (Data) | Nhan du lieu tu thiet bi (HTTP POST) |

---

## API Reference

### Gui du lieu tu thiet bi
```bash
curl -X POST "http://localhost:7896/iot/json?k=cruzrtwin2026&i=temp_sensor_001" \
  -H "Content-Type: application/json" \
  -H "fiware-service: cruzrtwin" \
  -H "fiware-servicepath: /" \
  -d '{"t": 28.5, "bat": 82}'
```

### Xem entity tren Orion
```bash
curl "http://localhost:1026/v2/entities" \
  -H "fiware-service: cruzrtwin" \
  -H "fiware-servicepath: /"
```

### Xem devices da dang ky
```bash
curl "http://localhost:4041/iot/devices" \
  -H "fiware-service: cruzrtwin" \
  -H "fiware-servicepath: /"
```

---

## Demo Scenarios

### iot_simulator_demo.py chay 3 pha:

1. **Normal (20s)**: Tat ca sensor gui data on dinh
2. **Fire Risk (30s)**: Nhiet do tang 25->48C, khoi 35->350ppm, do am giam
3. **Recovery (15s)**: Cac chi so giam dan ve binh thuong

Sau moi pha, script doc lai entity tu Orion de xac nhan data flow.

---

## Ghi chu

- API Key: `cruzrtwin2026`
- FIWARE Service: `cruzrtwin`
- IoT Agent luu registry trong MongoDB (database: iotagentjson)
- Can chay `provision_devices.py` mot lan dau tien
- Neu restart Docker, can provision lai
