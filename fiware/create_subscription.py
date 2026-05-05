import requests
import json

BASE_URL = "http://localhost:1026/v2"

# Định nghĩa subscription để theo dõi bất thường
subscription = {
    "description": "Temperature anomaly alert",
    "subject": {
        "entities": [
            {
                "idPattern": "urn:ngsi-ld:TemperatureSensor:.*",
                "type": "TemperatureSensor"
            }
        ],
        "condition": {
            "attrs": ["temperature"]
        }
    },
    "notification": {
        "http": {
            "url": "http://host.docker.internal:8000/webhook/fiware"
        },
        "attrs": ["temperature", "TimeInstant"]
    },
    "throttling": 5
}

# Tạo subscription
url = f"{BASE_URL}/subscriptions"
headers = {"Content-Type": "application/json"}

response = requests.post(url, headers=headers, json=subscription)

if response.status_code == 201:
    subscription_id = response.headers.get('Location', '').split('/')[-1]
    print(f"Subscription created: {subscription_id}")
else:
    print(f"Failed: {response.status_code} - {response.text}")

# Liệt kê tất cả subscriptions
print("\n📋 Current subscriptions:")
response = requests.get(f"{BASE_URL}/subscriptions")
subscriptions = response.json()
for sub in subscriptions:
    print(f"   - {sub.get('id')}: {sub.get('description')}")