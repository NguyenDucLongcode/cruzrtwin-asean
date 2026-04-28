from datetime import datetime, timedelta
import asyncio
from pathlib import Path
import sys

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from services import alert_service


class _FixedDateTime:
    current = datetime(2026, 4, 28, 18, 30, 0)

    @classmethod
    def now(cls):
        return cls.current


def test_process_anomaly_alert_debounces_duplicate_alerts(monkeypatch):
    monkeypatch.setattr(alert_service, "is_anomaly", lambda *args, **kwargs: True)
    monkeypatch.setattr(
        alert_service,
        "classify_anomaly",
        lambda *args, **kwargs: {
            "type": "air_quality",
            "severity": "high",
            "message": "duplicate alert",
            "action": "notify",
            "robot_instruction": "check room",
        },
    )

    sent_alerts = []

    async def fake_send_to_robot_queue(alert):
        sent_alerts.append(dict(alert))
        return True

    monkeypatch.setattr(alert_service, "send_to_robot_queue", fake_send_to_robot_queue)
    monkeypatch.setattr(alert_service, "store_alert", lambda alert: None)

    monkeypatch.setattr(alert_service, "datetime", _FixedDateTime)

    payload = {
        "data": [
            {
                "id": "sensor_001",
                "temperature": {"value": 30},
                "humidity": {"value": 70},
                "smokeLevel": {"value": 5},
                "co2": {"value": 900},
                "power": {"value": 12},
            }
        ]
    }

    first = asyncio.run(alert_service.process_anomaly_alert(payload))
    assert len(first) == 1
    assert len(sent_alerts) == 1

    _FixedDateTime.current = _FixedDateTime.current + timedelta(seconds=10)

    second = asyncio.run(alert_service.process_anomaly_alert(payload))
    assert len(second) == 0
    assert len(sent_alerts) == 1
