import requests
import time
from datetime import datetime, timedelta

FIWARE_URL = "http://localhost:1026/v2"
DEVICE_ID = "matter_smartplug_001"

# 1. Tạo entity
print("1. Creating smart plug...")
entity = {
    "id": DEVICE_ID,
    "type": "SmartPlug",
    "power": {"type": "Number", "value": 110},
    "onOff": {"type": "Boolean", "value": True}
}
requests.delete(f"{FIWARE_URL}/entities/{DEVICE_ID}")
requests.post(f"{FIWARE_URL}/entities", json=entity)

# 2. Inject nhiều lần để tạo lịch sử idle
print("\n2. Injecting idle history (35 minutes)...")

# Các mốc thời gian (phút trước)
times = [
    (35, 7.5),   # 35p trước
    (30, 7.5),   # 30p trước
    (25, 7.5),   # 25p trước
    (20, 7.5),   # 20p trước
    (15, 7.5),   # 15p trước
    (10, 7.5),   # 10p trước
    (5, 7.5),    # 5p trước
    (0, 7.5),    # hiện tại
]

for minutes_ago, power in times:
    timestamp = (datetime.now() - timedelta(minutes=minutes_ago)).isoformat() + "Z"
    payload = {
        "TimeInstant": {"type": "DateTime", "value": timestamp},
        "power": {"type": "Number", "value": power}
    }
    r = requests.patch(f"{FIWARE_URL}/entities/{DEVICE_ID}/attrs", json=payload)
    print(f"   {minutes_ago} min ago: {power}W → {r.status_code}")
    time.sleep(0.3)

print("\n  Done! Idle history injected (35 minutes)")
print("   Subscription will trigger webhook on each update")
print("   After 30 minutes idle, robot will be notified")