"""
FIWARE IoT Agent JSON — Device Provisioning
Dang ky service group va 5 loai thiet bi IoT voi IoT Agent.

Chay SAU khi docker-compose da up:
  python fiware/provision_devices.py
"""

import requests
import json
import sys

# ================== CONFIG ==================
IOT_AGENT_URL = "http://localhost:4041"
ORION_URL = "http://localhost:1026"
API_KEY = "cruzrtwin2026"
FIWARE_SERVICE = "cruzrtwin"
FIWARE_SERVICEPATH = "/"

HEADERS = {
    "Content-Type": "application/json",
    "fiware-service": FIWARE_SERVICE,
    "fiware-servicepath": FIWARE_SERVICEPATH
}


def check_services():
    """Kiem tra IoT Agent va Orion dang chay."""
    print("Kiem tra ket noi...")

    try:
        r = requests.get(f"{ORION_URL}/version", timeout=5)
        print(f"   Orion: OK (status {r.status_code})")
    except Exception as e:
        print(f"   Orion: KHONG KET NOI DUOC - {e}")
        print("   -> Chay: docker compose -f fiware/docker-compose.yml up -d")
        sys.exit(1)

    try:
        r = requests.get(f"{IOT_AGENT_URL}/iot/about", timeout=5)
        print(f"   IoT Agent: OK (status {r.status_code})")
    except Exception as e:
        print(f"   IoT Agent: KHONG KET NOI DUOC - {e}")
        print("   -> Chay: docker compose -f fiware/docker-compose.yml up -d")
        sys.exit(1)

    print()


def create_service_group():
    """Tao service group voi API key."""
    print("Tao service group...")

    payload = {
        "services": [
            {
                "apikey": API_KEY,
                "cbroker": f"http://orion:1026",
                "entity_type": "Thing",
                "resource": "/iot/json"
            }
        ]
    }

    url = f"{IOT_AGENT_URL}/iot/services"
    r = requests.post(url, headers=HEADERS, json=payload)

    if r.status_code == 201:
        print(f"   Service group created (API key: {API_KEY})")
    elif r.status_code == 409:
        print(f"   Service group da ton tai (API key: {API_KEY})")
    else:
        print(f"   Loi: {r.status_code} - {r.text}")

    print()


def provision_devices():
    """Dang ky 5 loai thiet bi IoT."""
    print("Dang ky thiet bi...")

    devices = [
        # 1. Temperature Sensor
        {
            "device_id": "temp_sensor_001",
            "entity_name": "urn:ngsi-ld:TemperatureSensor:sensor_001",
            "entity_type": "TemperatureSensor",
            "protocol": "PDI-IoTA-JSON",
            "transport": "HTTP",
            "attributes": [
                {"object_id": "t", "name": "temperature", "type": "Number"},
                {"object_id": "bat", "name": "battery", "type": "Number"}
            ],
            "static_attributes": [
                {"name": "location", "type": "Text", "value": "Room A - Server Room"},
                {"name": "status", "type": "Text", "value": "online"}
            ]
        },
        # 2. Humidity Sensor
        {
            "device_id": "hum_sensor_001",
            "entity_name": "urn:ngsi-ld:HumiditySensor:sensor_001",
            "entity_type": "HumiditySensor",
            "protocol": "PDI-IoTA-JSON",
            "transport": "HTTP",
            "attributes": [
                {"object_id": "h", "name": "humidity", "type": "Number"},
                {"object_id": "bat", "name": "battery", "type": "Number"}
            ],
            "static_attributes": [
                {"name": "location", "type": "Text", "value": "Room A - Server Room"},
                {"name": "status", "type": "Text", "value": "online"}
            ]
        },
        # 3. Smoke Sensor
        {
            "device_id": "smoke_sensor_001",
            "entity_name": "urn:ngsi-ld:SmokeSensor:sensor_001",
            "entity_type": "SmokeSensor",
            "protocol": "PDI-IoTA-JSON",
            "transport": "HTTP",
            "attributes": [
                {"object_id": "s", "name": "smokeLevel", "type": "Number"},
                {"object_id": "bat", "name": "battery", "type": "Number"}
            ],
            "static_attributes": [
                {"name": "location", "type": "Text", "value": "Room A - Server Room"},
                {"name": "status", "type": "Text", "value": "online"}
            ]
        },
        # 4. Air Quality Sensor
        {
            "device_id": "air_sensor_001",
            "entity_name": "urn:ngsi-ld:AirQualitySensor:sensor_001",
            "entity_type": "AirQualitySensor",
            "protocol": "PDI-IoTA-JSON",
            "transport": "HTTP",
            "attributes": [
                {"object_id": "co2", "name": "co2", "type": "Number"},
                {"object_id": "pm25", "name": "pm25", "type": "Number"},
                {"object_id": "tvoc", "name": "tvoc", "type": "Number"}
            ],
            "static_attributes": [
                {"name": "location", "type": "Text", "value": "Room B - Lobby"},
                {"name": "status", "type": "Text", "value": "online"}
            ]
        },
        # 5. Smart Plug
        {
            "device_id": "plug_001",
            "entity_name": "urn:ngsi-ld:SmartPlug:plug_001",
            "entity_type": "SmartPlug",
            "protocol": "PDI-IoTA-JSON",
            "transport": "HTTP",
            "attributes": [
                {"object_id": "p", "name": "power", "type": "Number"},
                {"object_id": "v", "name": "voltage", "type": "Number"},
                {"object_id": "c", "name": "current", "type": "Number"},
                {"object_id": "on", "name": "onOff", "type": "Boolean"},
                {"object_id": "e", "name": "energyToday", "type": "Number"}
            ],
            "static_attributes": [
                {"name": "location", "type": "Text", "value": "Room A - Server Room"},
                {"name": "status", "type": "Text", "value": "online"}
            ]
        }
    ]

    url = f"{IOT_AGENT_URL}/iot/devices"

    for device in devices:
        payload = {"devices": [device]}
        r = requests.post(url, headers=HEADERS, json=payload)

        if r.status_code == 201:
            print(f"   REGISTERED: {device['device_id']} -> {device['entity_name']}")
        elif r.status_code == 409:
            print(f"   DA TON TAI: {device['device_id']}")
        else:
            print(f"   LOI {device['device_id']}: {r.status_code} - {r.text}")

    print()


def verify_devices():
    """Kiem tra devices da duoc dang ky."""
    print("Xac nhan devices da dang ky...")

    url = f"{IOT_AGENT_URL}/iot/devices"
    r = requests.get(url, headers=HEADERS)

    if r.status_code == 200:
        data = r.json()
        devices = data.get("devices", [])
        print(f"   Tong so devices: {len(devices)}")
        for d in devices:
            print(f"   - {d['device_id']} -> {d['entity_name']} ({d['entity_type']})")
    else:
        print(f"   Loi: {r.status_code}")

    print()

    # Kiem tra entities tren Orion
    print("Kiem tra entities tren Orion...")
    orion_headers = {
        "fiware-service": FIWARE_SERVICE,
        "fiware-servicepath": FIWARE_SERVICEPATH
    }
    r = requests.get(f"{ORION_URL}/v2/entities", headers=orion_headers)
    if r.status_code == 200:
        entities = r.json()
        print(f"   Tong so entities: {len(entities)}")
        for e in entities:
            print(f"   - {e['id']} (type: {e['type']})")
    else:
        print(f"   Loi: {r.status_code}")


# ================== MAIN ==================
if __name__ == "__main__":
    print("=" * 60)
    print("FIWARE IoT Agent JSON — Device Provisioning")
    print("=" * 60)
    print()

    check_services()
    create_service_group()
    provision_devices()
    verify_devices()

    print("=" * 60)
    print("PROVISIONING HOAN THANH!")
    print()
    print("Buoc tiep theo:")
    print("   python fiware/iot_simulator.py        # Chay simulator realtime")
    print("   python fiware/iot_simulator_demo.py   # Chay demo 3 scenario")
    print("=" * 60)
