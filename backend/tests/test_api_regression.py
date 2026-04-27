from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import main
import api.sensors as sensors_api
import api.risk as risk_api
import services.energy_service as energy_service
from services.fiware_service import parse_entity_to_sensor


def _ngsi_attr(attr_type, value):
    return {"type": attr_type, "value": value}


@pytest.fixture()
def sample_entities():
    return [
        {
            "id": "matter_temp_sensor_001",
            "type": "TemperatureSensor",
            "TimeInstant": _ngsi_attr("DateTime", "2026-04-27T11:00:00Z"),
            "temperature": _ngsi_attr("Number", 29.1),
            "battery": _ngsi_attr("Number", 95),
            "status": _ngsi_attr("Text", "online"),
        },
        {
            "id": "matter_airquality_001",
            "type": "AirQualitySensor",
            "TimeInstant": _ngsi_attr("DateTime", "2026-04-27T11:00:00Z"),
            "pm25": _ngsi_attr("Number", 40.3),
            "pm10": _ngsi_attr("Number", 66.9),
            "co2": _ngsi_attr("Number", 431),
            "tvoc": _ngsi_attr("Number", 173),
            "aqi": _ngsi_attr("Integer", 142),
            "battery": _ngsi_attr("Number", 100),
            "status": _ngsi_attr("Text", "online"),
        },
        {
            "id": "matter_smartplug_001",
            "type": "SmartPlug",
            "TimeInstant": _ngsi_attr("DateTime", "2026-04-27T11:00:00Z"),
            "power": _ngsi_attr("Number", 7.5),
            "voltage": _ngsi_attr("Number", 220.0),
            "current": _ngsi_attr("Number", 0.034),
            "energyToday": _ngsi_attr("Number", 1.2),
            "onOff": _ngsi_attr("Boolean", True),
            "status": _ngsi_attr("Text", "online"),
        },
    ]


@pytest.fixture(autouse=True)
def mock_orion_data(monkeypatch, sample_entities):
    entities_by_id = {item["id"]: item for item in sample_entities}

    monkeypatch.setattr(sensors_api, "get_entities", lambda: sample_entities)
    monkeypatch.setattr(sensors_api, "get_entity_by_id", lambda device_id: entities_by_id.get(device_id))

    monkeypatch.setattr(risk_api, "get_entities", lambda: sample_entities)
    monkeypatch.setattr(risk_api, "get_entity_by_id", lambda device_id: entities_by_id.get(device_id))


@pytest.fixture()
def client():
    return TestClient(main.app)


def test_health_reports_orion_up(client, monkeypatch):
    class _Resp:
        status_code = 200

    monkeypatch.setattr("requests.get", lambda *args, **kwargs: _Resp())

    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["orion"] == "up"


def test_get_all_sensors_returns_extended_fields(client):
    response = client.get("/api/sensors/")
    assert response.status_code == 200

    sensors = response.json()
    assert len(sensors) == 3

    air = next(item for item in sensors if item["device_id"] == "matter_airquality_001")
    assert air["pm25"] == 40.3
    assert air["tvoc"] == 173.0
    assert air["aqi"] == 142

    plug = next(item for item in sensors if item["device_id"] == "matter_smartplug_001")
    assert plug["power"] == 7.5
    assert plug["voltage"] == 220.0
    assert plug["current"] == 0.034
    assert plug["energyToday"] == 1.2
    assert plug["onOff"] is True


def test_get_sensor_by_id_and_not_found(client):
    ok_resp = client.get("/api/sensors/matter_temp_sensor_001")
    assert ok_resp.status_code == 200
    assert ok_resp.json()["device_type"] == "TemperatureSensor"

    missing_resp = client.get("/api/sensors/not_found")
    assert missing_resp.status_code == 404


def test_risk_summary_route_works(client):
    response = client.get("/api/risk/summary")
    assert response.status_code == 200

    body = response.json()
    assert body["summary"]["total_devices"] == 3
    assert isinstance(body["devices"], list)


def test_risk_detail_route_works(client):
    response = client.get("/api/risk/matter_airquality_001")
    assert response.status_code == 200

    body = response.json()
    assert body["device_id"] == "matter_airquality_001"
    assert "risk" in body
    assert "score" in body["risk"]


def test_energy_endpoints_ai_mode(client, monkeypatch):
    class FakeOptimizer:
        def process_and_recommend(self, device_data):
            return {
                "timestamp": "2026-04-27T11:00:00Z",
                "total_devices_analyzed": len([d for d in device_data if d.get("onOff")]),
                "idle_devices_found": 1,
                "estimated_daily_savings_kwh": 0.12,
                "recommendations": ["Turn off matter_smartplug_001"],
                "fiware_commands": [
                    {
                        "command": "toggle_smart_plug",
                        "device_id": "matter_smartplug_001",
                        "action": "off",
                    }
                ],
            }

    monkeypatch.setattr(energy_service, "_get_energy_optimizer", lambda: FakeOptimizer())

    analysis_resp = client.get("/api/energy/analysis")
    assert analysis_resp.status_code == 200
    analysis = analysis_resp.json()
    assert analysis["mode"] == "ai"
    assert analysis["meta"]["idle_devices_found"] == 1
    assert analysis["fiware_commands"][0]["command"] == "toggle_smart_plug"

    stats_resp = client.get("/api/energy/stats")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert "total_power" in stats
    assert "idle_devices" in stats


def test_energy_execute_endpoint_uses_ai_commands_in_dry_run(client, monkeypatch):
    monkeypatch.setattr(
        energy_service,
        "get_energy_analysis",
        lambda: {
            "fiware_commands": [
                {
                    "command": "toggle_smart_plug",
                    "device_id": "matter_smartplug_001",
                    "payload": {"onOff": {"type": "Boolean", "value": False}},
                }
            ]
        },
    )

    response = client.post("/api/energy/execute", json={"dry_run": True})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["source"] == "ai-analysis"
    assert body["dry_run"] is True
    assert body["total_commands"] == 1
    assert body["executed"] == 1
    assert body["results"][0]["message"].startswith("Dry-run")


def test_energy_execute_endpoint_with_custom_commands(client, monkeypatch):
    def _fake_execute(command, dry_run=True):
        assert dry_run is False
        return {
            "success": True,
            "device_id": command.get("device_id"),
            "command": command.get("command"),
            "status_code": 204,
            "message": "Executed",
            "dry_run": False,
        }

    monkeypatch.setattr(energy_service, "execute_fiware_command", _fake_execute)

    payload = {
        "dry_run": False,
        "commands": [
            {
                "command": "toggle_smart_plug",
                "device_id": "matter_smartplug_001",
                "payload": {"onOff": {"type": "Boolean", "value": True}},
            }
        ],
    }

    response = client.post("/api/energy/execute", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["source"] == "request"
    assert body["dry_run"] is False
    assert body["executed"] == 1
    assert body["failed"] == 0
    assert body["results"][0]["status_code"] == 204


def test_websocket_ping_pong(client):
    with client.websocket_connect("/ws") as websocket:
        hello = websocket.receive_json()
        assert hello["type"] == "connection"

        websocket.send_text("ping")
        pong = websocket.receive_json()
        assert pong["type"] == "pong"
