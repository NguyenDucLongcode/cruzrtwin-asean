"""
Create a FIWARE Orion subscription that forwards entity changes to QuantumLeap,
so historical time-series data is persisted in CrateDB.
"""

import requests

FIWARE_ORION_URL = "http://localhost:1026/v2"
QUANTUMLEAP_NOTIFY_URL = "http://quantumleap:8668/v2/notify"
SUB_DESCRIPTION = "Timeseries forwarding to QuantumLeap"

subscription_payload = {
    "description": SUB_DESCRIPTION,
    "subject": {
        "entities": [
            {
                "idPattern": ".*",
            }
        ],
        "condition": {
            "attrs": [
                "TimeInstant",
                "power",
                "onOff",
                "temperature",
                "humidity",
                "smokeLevel",
                "co2",
                "pm25",
                "pm10",
                "tvoc",
                "aqi",
                "energyToday",
                "voltage",
                "current",
                "status",
            ]
        },
    },
    "notification": {
        "http": {
            "url": QUANTUMLEAP_NOTIFY_URL,
        }
    },
    "throttling": 1,
}


def list_subscriptions():
    response = requests.get(f"{FIWARE_ORION_URL}/subscriptions", timeout=10)
    if response.status_code != 200:
        return []
    return response.json()


def delete_existing_timeseries_subscriptions():
    subscriptions = list_subscriptions()
    for sub in subscriptions:
        if sub.get("description") == SUB_DESCRIPTION:
            sub_id = sub.get("id")
            requests.delete(f"{FIWARE_ORION_URL}/subscriptions/{sub_id}", timeout=10)
            print(f"Deleted old timeseries subscription: {sub_id}")


def create_subscription():
    response = requests.post(
        f"{FIWARE_ORION_URL}/subscriptions",
        json=subscription_payload,
        timeout=10,
    )
    if response.status_code == 201:
        sub_id = response.headers.get("Location", "").split("/")[-1]
        print(f"Created timeseries subscription: {sub_id}")
        return True

    print(f"Failed to create subscription: {response.status_code}")
    print(response.text)
    return False


if __name__ == "__main__":
    print("=" * 60)
    print("Creating Orion -> QuantumLeap timeseries subscription")
    print("=" * 60)
    delete_existing_timeseries_subscriptions()
    ok = create_subscription()
    if ok:
        print("Done. Orion updates will be persisted to QuantumLeap/CrateDB.")
        print("Query example: http://localhost:8668/v2/entities/<entityId>/attrs/power?lastN=20")
