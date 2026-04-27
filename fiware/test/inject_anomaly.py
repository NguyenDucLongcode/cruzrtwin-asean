import requests
import json
import time
from datetime import datetime

FIWARE_ORION_URL = "http://localhost:1026/v2"

def inject_high_temperature(device_id="matter_temp_sensor_001", temp=40.0):
    """Inject nhiệt độ cao (>35°C)"""
    url = f"{FIWARE_ORION_URL}/entities/{device_id}/attrs"
    payload = {
        "temperature": {
            "type": "Number",
            "value": temp
        }
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.patch(url, headers=headers, json=payload)
    print(f"🌡️ Injected temperature: {temp}°C → {response.status_code}")
    return response.status_code == 204

def inject_high_smoke(device_id="matter_smoke_sensor_001", smoke=350):
    """Inject khói cao (>300ppm)"""
    url = f"{FIWARE_ORION_URL}/entities/{device_id}/attrs"
    payload = {
        "smokeLevel": {
            "type": "Number",
            "value": smoke
        }
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.patch(url, headers=headers, json=payload)
    print(f"🔥 Injected smoke: {smoke}ppm → {response.status_code}")
    return response.status_code == 204

def inject_high_co2(device_id="matter_airquality_001", co2=1200):
    """Inject CO2 cao (>1000ppm)"""
    url = f"{FIWARE_ORION_URL}/entities/{device_id}/attrs"
    payload = {
        "co2": {
            "type": "Number",
            "value": co2
        }
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.patch(url, headers=headers, json=payload)
    print(f"💨 Injected CO2: {co2}ppm → {response.status_code}")
    return response.status_code == 204

def reset_to_normal():
    """Reset về giá trị bình thường"""
    print("\n🔄 Resetting to normal values...")
    
    # Reset temperature
    url = f"{FIWARE_ORION_URL}/entities/matter_temp_sensor_001/attrs"
    payload = {"temperature": {"type": "Number", "value": 25.0}}
    requests.patch(url, json=payload)
    
    # Reset smoke
    url = f"{FIWARE_ORION_URL}/entities/matter_smoke_sensor_001/attrs"
    payload = {"smokeLevel": {"type": "Number", "value": 50}}
    requests.patch(url, json=payload)
    
    # Reset CO2
    url = f"{FIWARE_ORION_URL}/entities/matter_airquality_001/attrs"
    payload = {"co2": {"type": "Number", "value": 420}}
    requests.patch(url, json=payload)
    
    print("✅ Reset complete")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 T-16: Testing Anomaly Injection")
    print("=" * 60)
    
    # Test high temperature
    print("\n📊 Test 1: High Temperature (40°C)")
    print(f"   Time: {datetime.now().isoformat()}")
    inject_high_temperature(temp=40.0)
    time.sleep(1)
    
    print("\n📊 Test 2: High Smoke (350ppm)")
    print(f"   Time: {datetime.now().isoformat()}")
    inject_high_smoke(smoke=350)
    time.sleep(1)
    
    print("\n📊 Test 3: High CO2 (1200ppm)")
    print(f"   Time: {datetime.now().isoformat()}")
    inject_high_co2(co2=1200)
    
    print("\n" + "=" * 60)
    print("✅ Anomaly injection complete!")
    print("   Check backend logs for alert notifications")
    print("=" * 60)
    
    # Ask to reset
    input("\nPress Enter to reset to normal values...")
    reset_to_normal()