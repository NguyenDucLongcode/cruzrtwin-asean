import requests
import json
import os
import time

BASE_URL = "http://localhost:1026/v2"

# ROOT PROJECT
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENTITY_DIR = os.path.join(ROOT_DIR, "data-models", "entities")

# =========================
# CONFIG
# =========================
ENTITY_ID = "urn:ngsi-ld:TemperatureSensor:sensor_001"

def create_entity(entity_file):
    if not os.path.exists(entity_file):
        raise FileNotFoundError(f"Not found: {entity_file}")

    with open(entity_file, "r", encoding="utf-8") as f:
        entity = json.load(f)

    url = f"{BASE_URL}/entities"
    headers = {"Content-Type": "application/json"}

    r = requests.post(url, headers=headers, json=entity)
    return r.status_code in [201, 204]


def get_entity(entity_id):
    url = f"{BASE_URL}/entities/{entity_id}"
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None


def update_entity(entity_id, attr, value):
    url = f"{BASE_URL}/entities/{entity_id}/attrs"
    payload = {
        attr: {
            "type": "Number",
            "value": value
        }
    }
    r = requests.patch(url, json=payload)
    return r.status_code == 204


# CHỈ DELETE KHI BẠN MUỐN RESET
def delete_entity(entity_id):
    url = f"{BASE_URL}/entities/{entity_id}"
    r = requests.delete(url)
    return r.status_code == 204


# =========================
# TEST FLOW (SAFE)
# =========================
print("=" * 60)
print("FIWARE SAFE CRUD TEST")
print("=" * 60)

print("\n1. CREATE entity...")
entity_path = os.path.join(ENTITY_DIR, "TemperatureSensor.json")

if create_entity(entity_path):
    print("   Created")
else:
    print("   Already exists or failed")

time.sleep(1)

print("\n2. READ entity...")
data = get_entity(ENTITY_ID)

if data:
    temp = data.get("temperature", {}).get("value")
    print(f"   Temperature = {temp}°C")
else:
    print("   Not found")

print("\n3. UPDATE entity...")
if update_entity(ENTITY_ID, "temperature", 26.5):
    print("   Updated temperature = 26.5°C")
else:
    print("   Update failed")

print("\n4. FINAL CHECK...")
data = get_entity(ENTITY_ID)

if data:
    print("   Entity still exists in Orion")
else:
    print("   Missing")

print("\n" + "=" * 60)
print("DONE (NO DELETE - DATA KEPT IN FIWARE)")
print("=" * 60)