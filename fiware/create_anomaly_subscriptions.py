# fiware/create_anomaly_subscriptions.py
"""
T-16: Tạo subscriptions trong FIWARE để trigger alerts khi có bất thường
"""

import requests
import json

FIWARE_ORION_URL = "http://localhost:1026/v2"
BACKEND_WEBHOOK_URL = "http://host.docker.internal:8000/api/webhook/anomaly"

# Subscription cho nhiệt độ cao (temperature > 35°C)
# ⚠️ KHÔNG dùng ký tự đặc biệt như >, °C trong description
temperature_subscription = {
    "description": "Alert high temperature threshold exceeded",
    "subject": {
        "entities": [
            {
                "idPattern": "matter_temp.*",
                "type": "TemperatureSensor"
            }
        ],
        "condition": {
            "attrs": ["temperature"],
            "expression": {
                "q": "temperature>35"
            }
        }
    },
    "notification": {
        "http": {
            "url": BACKEND_WEBHOOK_URL
        },
        "attrs": ["temperature", "TimeInstant"]
    },
    "throttling": 5
}

# Subscription cho khói cao (smoke > 300ppm)
smoke_subscription = {
    "description": "Alert high smoke level threshold exceeded",
    "subject": {
        "entities": [
            {
                "idPattern": "matter_smoke.*",
                "type": "SmokeSensor"
            }
        ],
        "condition": {
            "attrs": ["smokeLevel"],
            "expression": {
                "q": "smokeLevel>300"
            }
        }
    },
    "notification": {
        "http": {
            "url": BACKEND_WEBHOOK_URL
        },
        "attrs": ["smokeLevel", "TimeInstant"]
    },
    "throttling": 5
}

# Subscription cho CO2 cao (CO2 > 1000ppm)
co2_subscription = {
    "description": "Alert high CO2 level threshold exceeded",
    "subject": {
        "entities": [
            {
                "idPattern": "matter_airquality.*",
                "type": "AirQualitySensor"
            }
        ],
        "condition": {
            "attrs": ["co2"],
            "expression": {
                "q": "co2>1000"
            }
        }
    },
    "notification": {
        "http": {
            "url": BACKEND_WEBHOOK_URL
        },
        "attrs": ["co2", "TimeInstant"]
    },
    "throttling": 5
}

def create_subscription(subscription):
    """Tạo subscription trong Orion"""
    url = f"{FIWARE_ORION_URL}/subscriptions"
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, headers=headers, json=subscription)
    
    if response.status_code == 201:
        location = response.headers.get('Location', '')
        sub_id = location.split('/')[-1]
        print(f"   ✅ Created: {subscription['description']} (ID: {sub_id})")
        return sub_id
    else:
        print(f"   ❌ Failed: {subscription['description']} - {response.status_code}")
        print(f"      {response.text}")
        return None

def list_subscriptions():
    """Liệt kê tất cả subscriptions"""
    url = f"{FIWARE_ORION_URL}/subscriptions"
    response = requests.get(url)
    
    if response.status_code == 200:
        subs = response.json()
        print(f"\n📋 Current subscriptions ({len(subs)}):")
        for sub in subs:
            print(f"   - {sub.get('id')}: {sub.get('description')}")
        return subs
    return []

def delete_all_subscriptions():
    """Xóa tất cả subscriptions (cleanup)"""
    subs = list_subscriptions()
    for sub in subs:
        sub_id = sub.get('id')
        url = f"{FIWARE_ORION_URL}/subscriptions/{sub_id}"
        response = requests.delete(url)
        if response.status_code == 204:
            print(f"   🗑️ Deleted: {sub_id}")
        else:
            print(f"   ❌ Failed to delete: {sub_id}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔔 T-16: Creating FIWARE Subscriptions for Anomaly Alerts")
    print("=" * 60)
    
    # Cleanup old subscriptions
    print("\n🧹 Cleaning up old subscriptions...")
    delete_all_subscriptions()
    
    # Create new subscriptions
    print("\n📝 Creating new subscriptions...")
    temp_id = create_subscription(temperature_subscription)
    smoke_id = create_subscription(smoke_subscription)
    co2_id = create_subscription(co2_subscription)
    
    # List all
    list_subscriptions()
    
    print("\n" + "=" * 60)
    print("✅ Subscriptions created successfully!")
    print("   - Temperature greater than 35C → Alert")
    print("   - Smoke greater than 300ppm → Alert")
    print("   - CO2 greater than 1000ppm → Alert")
    print("=" * 60)