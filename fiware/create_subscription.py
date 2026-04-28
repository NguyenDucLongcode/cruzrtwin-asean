"""
T-16: Tạo subscription DUY NHẤT trong FIWARE (khuyến nghị)
→ Orion chỉ gửi data khi có thay đổi
→ Backend xử lý anomaly (cache + AI)
"""

import requests

FIWARE_ORION_URL = "http://localhost:1026/v2"
BACKEND_WEBHOOK_URL = "http://host.docker.internal:8000/api/webhook/anomaly"

# ========== UNIFIED SUBSCRIPTION (KHÔNG FILTER) ==========
unified_subscription = {
    "description": "Monitor ALL sensor changes - backend handles anomaly detection",
    "subject": {
        "entities": [
            {"idPattern": ".*", "type": "TemperatureSensor"},
            {"idPattern": ".*", "type": "SmokeSensor"},
            {"idPattern": ".*", "type": "AirQualitySensor"},
            {"idPattern": ".*", "type": "HumiditySensor"},
            {"idPattern": ".*", "type": "SmartPlug"}
        ],
        "condition": {
            # Trigger khi bất kỳ attribute nào thay đổi
            "attrs": ["temperature", "smokeLevel", "co2", "humidity", "power"]
        }
    },
    "notification": {
        "http": {
            "url": BACKEND_WEBHOOK_URL
        },
        # Gửi toàn bộ field có thể có (entity nào có gì thì gửi đó)
        "attrs": [
            "temperature",
            "smokeLevel",
            "co2",
            "humidity",
            "power",
            "TimeInstant"
        ],
        "metadata": ["unit"]
    },
    "throttling": 2  # Tối thiểu 2 giây giữa các notification để tránh spam
}


# ========== CORE FUNCTIONS ==========

def create_subscription(subscription):
    url = f"{FIWARE_ORION_URL}/subscriptions"
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, json=subscription)

    if response.status_code == 201:
        location = response.headers.get('Location', '')
        sub_id = location.split('/')[-1]
        print(f"   Created subscription (ID: {sub_id})")
        return sub_id
    else:
        print(f"   Failed - {response.status_code}")
        print(response.text)
        return None


def list_subscriptions():
    url = f"{FIWARE_ORION_URL}/subscriptions"
    response = requests.get(url)

    if response.status_code == 200:
        subs = response.json()
        print(f"\n Current subscriptions ({len(subs)}):")
        for sub in subs:
            print(f"   - {sub.get('id')[:8]}: {sub.get('description')}")
        return subs
    return []


def delete_all_subscriptions():
    subs = list_subscriptions()
    print(f"\n🧹 Deleting {len(subs)} subscriptions...")

    for sub in subs:
        sub_id = sub.get('id')
        url = f"{FIWARE_ORION_URL}/subscriptions/{sub_id}"
        response = requests.delete(url)

        if response.status_code == 204:
            print(f"   Deleted: {sub_id[:8]}")
        else:
            print(f"   Failed: {sub_id[:8]}")


# ========== MAIN ==========
if __name__ == "__main__":
    print("=" * 60)
    print(" FIWARE UNIFIED SUBSCRIPTION (BEST PRACTICE)")
    print("=" * 60)

    # 1. Xóa cũ
    print("\n Cleaning old subscriptions...")
    delete_all_subscriptions()

    # 2. Tạo mới
    print("\n Creating unified subscription...")
    create_subscription(unified_subscription)

    # 3. Kiểm tra
    list_subscriptions()

    print("\n" + "=" * 60)
    print("  Done!")
    print("   → Orion chỉ gửi data khi có thay đổi")
    print("   → Backend sẽ:")
    print("      - Cache dữ liệu (C1)")
    print("      - Combine nhiều sensor")
    print("      - Detect anomaly (AI)")
    print("=" * 60)