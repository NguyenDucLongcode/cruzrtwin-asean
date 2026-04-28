from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

ENERGY_DIR = BACKEND_DIR.parent / "ai-models" / "energy"
if str(ENERGY_DIR) not in sys.path:
    sys.path.insert(0, str(ENERGY_DIR))

import main
import api.webhook as webhook_api


@pytest.fixture()
def client():
    return TestClient(main.app)


def _livingroom_fiware_payload():
    return {
        "data": [
            {
                "id": "motion_sensor_livingroom_001",
                "type": "MotionSensor",
                "motion_detected": {"type": "Boolean", "value": True},
                "TimeInstant": {"type": "DateTime", "value": "2026-04-28T18:30:00Z"},
            },
            {
                "id": "smart_plug_tv_001",
                "type": "SmartPlug",
                "power": {"type": "Number", "value": 7.9},
                "onOff": {"type": "Boolean", "value": True},
                "TimeInstant": {"type": "DateTime", "value": "2026-04-28T18:35:00Z"},
            },
        ]
    }


def test_livingroom_webhook_forwards_fiware_payload(client, monkeypatch):
    captured = {}

    async def fake_process_livingroom_data(payload):
        captured["payload"] = payload
        return {
            "processed": len(payload.get("data", [])),
            "devices_tracked": 1,
        }

    monkeypatch.setattr(webhook_api, "process_livingroom_data", fake_process_livingroom_data)

    payload = _livingroom_fiware_payload()
    response = client.post("/api/webhook/livingroom", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["message"] == "Living room processed"
    assert body["processed"] == 2
    assert body["devices_tracked"] == 1
    assert captured["payload"] == payload


def test_livingroom_webhook_accepts_motion_only_payload(client, monkeypatch):
    async def fake_process_livingroom_data(payload):
        assert payload["data"][0]["type"] == "MotionSensor"
        return {"processed": 1, "devices_tracked": 0}

    monkeypatch.setattr(webhook_api, "process_livingroom_data", fake_process_livingroom_data)

    payload = {
        "data": [
            {
                "id": "motion_sensor_livingroom_002",
                "type": "MotionSensor",
                "motion_detected": {"type": "Boolean", "value": False},
                "TimeInstant": {"type": "DateTime", "value": "2026-04-28T18:40:00Z"},
            }
        ]
    }

    response = client.post("/api/webhook/livingroom", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["processed"] == 1
    assert body["devices_tracked"] == 0