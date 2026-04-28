import requests

FIWARE_URL = "http://localhost:1026/v2"
BACKEND_URL = "http://host.docker.internal:8000"

subscription = {
    "description": "Energy optimization - detect low power",
    "subject": {
        "entities": [
            {
                "idPattern": ".*SmartPlug.*",
                "type": "SmartPlug"
            }
        ],
        "condition": {
            "attrs": ["power"],
            "expression": {
                "q": "power<10"  # Khi công suất < 10W
            }
        }
    },
    "notification": {
        "http": {
            "url": f"{BACKEND_URL}/api/energy/check_idle"
        },
        "attrs": ["power", "TimeInstant"]
    },
    "throttling": 30  # Tối đa 1 notification/30 giây
}

response = requests.post(f"{FIWARE_URL}/subscriptions", json=subscription)
print(f"Created: {response.status_code}")