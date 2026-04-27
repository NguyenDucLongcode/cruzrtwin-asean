import requests
import time

FIWARE_URL = "http://localhost:1026/v2"
DEVICE_ID = "urn:ngsi-ld:SmartPlug:plug_001"

# Các mốc thời gian: 45p, 30p, 15p, 0p trước
times = [
    ("2026-04-27T10:15:00Z", 7.5),  # 45 phút trước
    ("2026-04-27T10:30:00Z", 7.5),  # 30 phút trước
    ("2026-04-27T10:45:00Z", 7.4),  # 15 phút trước
    ("2026-04-27T11:00:00Z", 7.5),  # hiện tại
]

print("Injecting idle history...")

for timestamp, power in times:
    payload = {
        "TimeInstant": {"type": "DateTime", "value": timestamp},
        "power": {"type": "Number", "value": power}
    }
    response = requests.patch(f"{FIWARE_URL}/entities/{DEVICE_ID}/attrs", json=payload)
    print(f"   {timestamp} → power={power}W → {response.status_code}")
    time.sleep(0.5)

print("\n Done! 4 records injected.")
print("Now call: curl http://localhost:8000/api/energy/analysis")