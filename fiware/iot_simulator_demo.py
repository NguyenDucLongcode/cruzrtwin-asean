"""
FIWARE IoT Simulator — Demo 3 Scenario
Demo gia lap IoT gui data qua IoT Agent JSON voi 3 pha:
  1. Normal operation (20 giay)
  2. Fire risk escalation (30 giay)
  3. Recovery (15 giay)

Chay SAU khi da provision devices:
  python fiware/iot_simulator_demo.py
"""

import requests
import numpy as np
import time
import sys
from datetime import datetime

# ================== CONFIG ==================
IOT_AGENT_SOUTH_URL = "http://localhost:7896/iot/json"
ORION_URL = "http://localhost:1026/v2"
API_KEY = "cruzrtwin2026"
FIWARE_SERVICE = "cruzrtwin"
FIWARE_SERVICEPATH = "/"
INTERVAL = 3  # giay

HEADERS_IOT = {
    "Content-Type": "application/json",
    "fiware-service": FIWARE_SERVICE,
    "fiware-servicepath": FIWARE_SERVICEPATH
}
HEADERS_ORION = {
    "fiware-service": FIWARE_SERVICE,
    "fiware-servicepath": FIWARE_SERVICEPATH
}


def send(device_id, payload):
    """Gui du lieu len IoT Agent."""
    url = f"{IOT_AGENT_SOUTH_URL}?k={API_KEY}&i={device_id}"
    try:
        r = requests.post(url, json=payload, headers=HEADERS_IOT, timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def check_orion_entity(entity_id):
    """Doc entity tu Orion de xac nhan du lieu."""
    try:
        r = requests.get(f"{ORION_URL}/entities/{entity_id}", headers=HEADERS_ORION, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def print_entity_snapshot(entity_id, label):
    """In nhanh gia tri entity tu Orion."""
    entity = check_orion_entity(entity_id)
    if entity:
        print(f"\n   ORION ENTITY: {entity_id}")
        for key, val in entity.items():
            if key in ('id', 'type'):
                continue
            if isinstance(val, dict) and 'value' in val:
                print(f"      {key}: {val['value']}")
    else:
        print(f"\n   Khong doc duoc entity {entity_id} tu Orion")


# ================== CHECK ==================
print("=" * 70)
print("CRUZRTWIN IoT SIMULATOR DEMO")
print("   3 Scenario: Normal -> Fire Risk -> Recovery")
print("=" * 70)

# Check connectivity
print("\nKiem tra ket noi...")
try:
    r = requests.get(f"{ORION_URL[:-3]}/version", timeout=5)
    print(f"   Orion: OK")
except Exception:
    print("   Orion: KHONG KET NOI")
    print("   -> Chay: docker compose -f fiware/docker-compose.yml up -d")
    sys.exit(1)

try:
    requests.get("http://localhost:4041/iot/about", timeout=5)
    print(f"   IoT Agent: OK")
except Exception:
    print("   IoT Agent: KHONG KET NOI")
    print("   -> Chay: docker compose -f fiware/docker-compose.yml up -d")
    sys.exit(1)

print()
total_sent = 0

# ============================================================
# SCENARIO 1: Normal Operation (20 giay)
# ============================================================
print("=" * 70)
print(" SCENARIO 1: HOAT DONG BINH THUONG (20 giay)")
print("-" * 70)
print("   Tat ca sensor gui du lieu on dinh trong gioi han binh thuong")
print()

ticks = 20 // INTERVAL
for i in range(ticks):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] Normal tick {i+1}/{ticks}")

    send("temp_sensor_001", {"t": round(25 + np.random.normal(0, 1), 2), "bat": 85})
    send("hum_sensor_001", {"h": round(65 + np.random.normal(0, 3), 2), "bat": 90})
    send("smoke_sensor_001", {"s": round(35 + np.random.normal(0, 5), 2), "bat": 78})
    send("air_sensor_001", {
        "co2": round(400 + np.random.normal(0, 15), 2),
        "pm25": round(15 + np.random.normal(0, 2), 2),
        "tvoc": round(50 + np.random.normal(0, 8), 2)
    })
    send("plug_001", {
        "p": round(45 + np.random.normal(0, 5), 2),
        "v": round(220 + np.random.normal(0, 1.5), 2),
        "c": round(0.2 + np.random.normal(0, 0.01), 3),
        "on": True,
        "e": round(1.2 + np.random.uniform(0, 0.3), 2)
    })
    total_sent += 5

    print(f"   temp=25C, hum=65%, smoke=35ppm, co2=400ppm (NORMAL)")
    time.sleep(INTERVAL)

print_entity_snapshot("urn:ngsi-ld:TemperatureSensor:sensor_001", "Normal")

# ============================================================
# SCENARIO 2: Fire Risk Escalation (30 giay)
# ============================================================
print("\n" + "=" * 70)
print(" SCENARIO 2: NGUY CO CHAY - ESCALATION (30 giay)")
print("-" * 70)
print("   Nhiet do tang dan 25->48C, khoi tang 35->350ppm")
print("   Do am giam 65->30%, CO2 tang")
print()

ticks = 30 // INTERVAL
for i in range(ticks):
    progress = i / ticks
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] FIRE RISK tick {i+1}/{ticks} (progress={progress:.0%})")

    temp = round(25 + progress * 23 + np.random.normal(0, 0.3), 2)
    hum = round(65 - progress * 35 + np.random.normal(0, 1), 2)
    smoke = round(35 + progress * 315 + np.random.normal(0, 2), 2)
    co2 = round(400 + progress * 400 + np.random.normal(0, 5), 2)

    send("temp_sensor_001", {"t": temp, "bat": 85})
    send("hum_sensor_001", {"h": hum, "bat": 90})
    send("smoke_sensor_001", {"s": smoke, "bat": 78})
    send("air_sensor_001", {"co2": co2, "pm25": round(15 + progress * 40, 2), "tvoc": round(50 + progress * 150, 2)})
    send("plug_001", {
        "p": round(45 + progress * 50 + np.random.normal(0, 3), 2),
        "v": round(220 + np.random.normal(0, 2), 2),
        "c": round(0.2 + progress * 0.3, 3),
        "on": True,
        "e": round(1.5 + progress * 2, 2)
    })
    total_sent += 5

    print(f"   temp={temp}C, hum={hum}%, smoke={smoke}ppm, co2={co2}ppm (ESCALATING)")
    time.sleep(INTERVAL)

print_entity_snapshot("urn:ngsi-ld:TemperatureSensor:sensor_001", "Fire Peak")
print_entity_snapshot("urn:ngsi-ld:SmokeSensor:sensor_001", "Fire Peak")

# ============================================================
# SCENARIO 3: Recovery (15 giay)
# ============================================================
print("\n" + "=" * 70)
print(" SCENARIO 3: PHUC HOI (15 giay)")
print("-" * 70)
print("   Cac chi so giam dan ve binh thuong")
print()

ticks = 15 // INTERVAL
for i in range(ticks):
    progress = i / ticks  # 0->1 = dang phuc hoi
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] RECOVERY tick {i+1}/{ticks}")

    # Giam tu gia tri cao ve binh thuong
    temp = round(48 - progress * 23 + np.random.normal(0, 0.5), 2)
    hum = round(30 + progress * 35 + np.random.normal(0, 1), 2)
    smoke = round(350 - progress * 315 + np.random.normal(0, 3), 2)
    co2 = round(800 - progress * 400 + np.random.normal(0, 10), 2)

    send("temp_sensor_001", {"t": temp, "bat": 85})
    send("hum_sensor_001", {"h": hum, "bat": 90})
    send("smoke_sensor_001", {"s": smoke, "bat": 78})
    send("air_sensor_001", {"co2": co2, "pm25": round(55 - progress * 40, 2), "tvoc": round(200 - progress * 150, 2)})
    send("plug_001", {
        "p": round(95 - progress * 50 + np.random.normal(0, 3), 2),
        "v": round(220 + np.random.normal(0, 1.5), 2),
        "c": round(0.5 - progress * 0.3, 3),
        "on": True,
        "e": round(3.5 - progress * 2, 2)
    })
    total_sent += 5

    print(f"   temp={temp}C, hum={hum}%, smoke={smoke}ppm (RECOVERING)")
    time.sleep(INTERVAL)

print_entity_snapshot("urn:ngsi-ld:TemperatureSensor:sensor_001", "Recovery")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("TONG KET DEMO IoT SIMULATOR")
print("=" * 70)
print(f"\n   Tong readings gui: {total_sent}")
print(f"   Devices: 5 (temp, humidity, smoke, air, plug)")
print(f"   Scenarios:")
print(f"      1. Normal:     20 giay - OK")
print(f"      2. Fire Risk:  30 giay - Nhiet do/khoi tang dan")
print(f"      3. Recovery:   15 giay - Tro ve binh thuong")
print(f"\n   Luong du lieu:")
print(f"      IoT Simulator -> IoT Agent (port 7896) -> FIWARE Orion (port 1026)")
print(f"\n   Kiem tra entity tren Orion:")
print(f"      curl http://localhost:1026/v2/entities -H 'fiware-service: cruzrtwin'")
print("\n" + "=" * 70)
