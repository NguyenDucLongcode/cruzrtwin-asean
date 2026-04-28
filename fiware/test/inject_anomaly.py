import requests
import json
import time
from datetime import datetime

FIWARE_ORION_URL = "http://localhost:1026/v2"
HEADERS = {"Content-Type": "application/json"}

# ==================== CHECK CONNECTION ====================

def check_fiware_connection():
    """Kiểm tra FIWARE Orion có chạy không"""
    print("   Checking FIWARE Orion connection...")
    try:
        response = requests.get(f"{FIWARE_ORION_URL}/entities", timeout=5)
        print("   FIWARE Orion is running\n")
        return True
    except requests.exceptions.ConnectionError:
        print(f"   Cannot connect to FIWARE Orion at {FIWARE_ORION_URL}")
        print("   Start it with: docker-compose -f fiware/docker-compose.yml up -d\n")
        return False
    except Exception as e:
        print(f"   Error: {e}\n")
        return False

# ==================== CREATE ENTITIES ====================

def create_test_entities():
    """Tạo các entity cảm biến nếu chưa tồn tại"""
    print("\n Creating test entities...")
    
    entities = [
        {
            "id": "matter_temp_sensor_001",
            "type": "TemperatureSensor",
            "temperature": {"type": "Number", "value": 25.0},
            "TimeInstant": {"type": "DateTime", "value": datetime.now().isoformat()}
        },
        {
            "id": "matter_smoke_sensor_001",
            "type": "SmokeSensor",
            "smokeLevel": {"type": "Number", "value": 50},
            "TimeInstant": {"type": "DateTime", "value": datetime.now().isoformat()}
        },
        {
            "id": "matter_airquality_001",
            "type": "AirQualitySensor",
            "co2": {"type": "Number", "value": 420},
            "TimeInstant": {"type": "DateTime", "value": datetime.now().isoformat()}
        }
    ]
    
    for entity in entities:
        # Xóa cũ nếu tồn tại (ignore 404 error nếu không tồn tại)
        try:
            del_response = requests.delete(
                f"{FIWARE_ORION_URL}/entities/{entity['id']}",
                headers=HEADERS,
                timeout=5
            )
            if del_response.status_code == 204:
                print(f"   Deleted old {entity['id']}")
        except Exception as e:
            print(f"   Could not delete {entity['id']}: {e}")
        
        # Tạo mới
        try:
            response = requests.post(
                f"{FIWARE_ORION_URL}/entities",
                json=entity,
                headers=HEADERS,
                timeout=5
            )
            if response.status_code == 201:
                print(f"   Created {entity['id']}")
            else:
                print(f"   Failed to create {entity['id']}: {response.status_code}")
                print(f"      Response: {response.text}")
        except Exception as e:
            print(f"   Error creating {entity['id']}: {e}")

# ==================== ANOMALY INJECTION FUNCTIONS ====================

def inject_high_temperature(device_id="matter_temp_sensor_001", temp=40.0):
    """Inject nhiệt độ cao (>35°C)"""
    try:
        url = f"{FIWARE_ORION_URL}/entities/{device_id}/attrs"
        payload = {"temperature": {"type": "Number", "value": temp}}
        response = requests.patch(url, headers=HEADERS, json=payload, timeout=5)
        if response.status_code == 204:
            print(f"   Injected temperature: {temp}°C")
            return True
        else:
            print(f"   Failed to inject temperature: {response.status_code}")
            print(f"      {response.text}")
            return False
    except Exception as e:
        print(f"   Error injecting temperature: {e}")
        return False

def inject_high_smoke(device_id="matter_smoke_sensor_001", smoke=350):
    """Inject khói cao (>300ppm)"""
    try:
        url = f"{FIWARE_ORION_URL}/entities/{device_id}/attrs"
        payload = {"smokeLevel": {"type": "Number", "value": smoke}}
        response = requests.patch(url, headers=HEADERS, json=payload, timeout=5)
        if response.status_code == 204:
            print(f"   Injected smoke: {smoke}ppm")
            return True
        else:
            print(f"   Failed to inject smoke: {response.status_code}")
            print(f"      {response.text}")
            return False
    except Exception as e:
        print(f"   Error injecting smoke: {e}")
        return False

def inject_high_co2(device_id="matter_airquality_001", co2=1200):
    """Inject CO2 cao (>1000ppm)"""
    try:
        url = f"{FIWARE_ORION_URL}/entities/{device_id}/attrs"
        payload = {"co2": {"type": "Number", "value": co2}}
        response = requests.patch(url, headers=HEADERS, json=payload, timeout=5)
        if response.status_code == 204:
            print(f"   Injected CO2: {co2}ppm")
            return True
        else:
            print(f"   Failed to inject CO2: {response.status_code}")
            print(f"      {response.text}")
            return False
    except Exception as e:
        print(f"   Error injecting CO2: {e}")
        return False

def reset_to_normal():
    """Reset về giá trị bình thường"""
    print("\n  Resetting to normal values...")
    
    resets = [
        ("matter_temp_sensor_001", {"temperature": {"type": "Number", "value": 25.0}}),
        ("matter_smoke_sensor_001", {"smokeLevel": {"type": "Number", "value": 50}}),
        ("matter_airquality_001", {"co2": {"type": "Number", "value": 420}})
    ]
    
    for entity_id, payload in resets:
        try:
            url = f"{FIWARE_ORION_URL}/entities/{entity_id}/attrs"
            response = requests.patch(url, headers=HEADERS, json=payload, timeout=5)
            if response.status_code == 204:
                print(f"   Reset {entity_id}")
            else:
                print(f"   Failed to reset {entity_id}: {response.status_code}")
        except Exception as e:
            print(f"   Error resetting {entity_id}: {e}")
    
    print("   Reset complete")

# ==================== MAIN ====================

if __name__ == "__main__":
    print("=" * 60)
    print("  T-16: Testing Anomaly Injection")
    print("=" * 60)
    
    # Check connection first
    if not check_fiware_connection():
        print(" Cannot proceed without FIWARE Orion connection")
        exit(1)
    
    # Bước 1: Tạo entities
    create_test_entities()
    time.sleep(1)
    
    # Bước 2: Inject anomalies
    print("\n  Injecting anomalies...")
    
    print("\n   Test 1: High Temperature (40°C)")
    print(f"   Time: {datetime.now().isoformat()}")
    inject_high_temperature(temp=40.0)
    time.sleep(1)
    
    print("\n   Test 2: High Smoke (350ppm)")
    print(f"   Time: {datetime.now().isoformat()}")
    inject_high_smoke(smoke=350)
    time.sleep(1)
    
    print("\n   Test 3: High CO2 (1200ppm)")
    print(f"   Time: {datetime.now().isoformat()}")
    inject_high_co2(co2=1200)
    
    print("\n" + "=" * 60)
    print(" Anomaly injection complete!")
    print("   Check backend logs for alert notifications")
    print("=" * 60)
    
    # Bước 3: Reset
    input("\nPress Enter to reset to normal values...")
    reset_to_normal()