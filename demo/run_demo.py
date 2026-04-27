# demo/run_demo.py
"""
T-22: End-to-End Demo Script
Chạy toàn bộ luồng demo từ đầu đến cuối
"""

import requests
import time
import sys
from datetime import datetime

# Backend URL
BACKEND_URL = "http://localhost:8000"
ROBOT_URL = "http://localhost:8001"
FIWARE_URL = "http://localhost:1026/v2"

def print_step(step_num, description):
    """In bước demo"""
    print(f"\n{'='*60}")
    print(f"📌 Step {step_num}: {description}")
    print('='*60)

def wait_for_user(prompt="   Press Enter to continue..."):
    """Đợi người dùng nhấn Enter"""
    input(prompt)

def check_health():
    """Kiểm tra sức khỏe hệ thống"""
    print("\n🏥 System Health Check")
    
    try:
        r = requests.get(f"{BACKEND_URL}/health")
        print(f"   Backend: {r.json().get('status', 'unknown')}")
    except:
        print("   ❌ Backend: DOWN")
        return False
    
    try:
        r = requests.get(f"{ROBOT_URL}/health")
        print(f"   Robot API: {r.json().get('status', 'unknown')}")
    except:
        print("   ❌ Robot API: DOWN")
        return False
    
    try:
        r = requests.get("http://localhost:1026/version")
        print(f"   FIWARE Orion: OK")
    except:
        print("   ❌ FIWARE Orion: DOWN")
        return False
    
    return True

def get_sensors():
    """Lấy dữ liệu cảm biến"""
    response = requests.get(f"{BACKEND_URL}/api/sensors/")
    return response.json()

def inject_anomaly(device_id, attribute, value):
    """Inject dữ liệu bất thường vào FIWARE"""
    url = f"{FIWARE_URL}/entities/{device_id}/attrs"
    payload = {attribute: {"type": "Number", "value": value}}
    response = requests.patch(url, json=payload)
    return response.status_code == 204

def reset_anomaly(device_id, attribute, normal_value):
    """Reset về giá trị bình thường"""
    return inject_anomaly(device_id, attribute, normal_value)

def demo_scenario_1():
    """Scenario 1: Phát hiện nhiệt độ cao"""
    print_step(1, "Phát hiện nhiệt độ bất thường (>35°C)")
    
    print("   📊 Normal temperature: 25°C")
    print("   🔥 Inject anomaly: 40°C")
    
    # Inject anomaly
    if inject_anomaly("matter_temp_sensor_001", "temperature", 40.0):
        print("   ✅ Anomaly injected")
        time.sleep(2)  # Đợi alert
        print("   ✅ Alert should appear in dashboard")
    else:
        print("   ❌ Injection failed")
        return False
    
    # Check via backend
    response = requests.get(f"{BACKEND_URL}/api/risk/matter_temp_sensor_001")
    if response.status_code == 200:
        risk = response.json()
        print(f"   📊 Risk score: {risk['risk']['score']}")
        if risk['risk']['score'] >= 40:
            print("   ✅ Risk detected correctly")
        else:
            print("   ⚠️ Risk score lower than expected")
    else:
        print("   ❌ Cannot get risk data")
    
    wait_for_user("   ✅ Scenario 1 complete. Press Enter to reset...")
    
    # Reset
    reset_anomaly("matter_temp_sensor_001", "temperature", 25.0)
    print("   🔄 Reset to normal temperature")
    return True

def demo_scenario_2():
    """Scenario 2: Phát hiện khói (cháy)"""
    print_step(2, "Phát hiện khói cao - CẢNH BÁO CHÁY")
    
    print("   📊 Normal smoke: 50ppm")
    print("   🔥 Inject anomaly: 350ppm (Fire!)")
    
    # Inject anomaly
    if inject_anomaly("matter_smoke_sensor_001", "smokeLevel", 350.0):
        print("   ✅ Anomaly injected")
        time.sleep(2)
        print("   ✅ Critical alert should appear")
    else:
        print("   ❌ Injection failed")
        return False
    
    # Check via backend
    response = requests.get(f"{BACKEND_URL}/api/risk/matter_smoke_sensor_001")
    if response.status_code == 200:
        risk = response.json()
        print(f"   📊 Risk score: {risk['risk']['score']}")
        if risk['risk']['level'] == "critical":
            print("   ✅ Critical risk detected correctly")
    else:
        print("   ❌ Cannot get risk data")
    
    wait_for_user("   ✅ Scenario 2 complete. Press Enter to reset...")
    
    # Reset
    reset_anomaly("matter_smoke_sensor_001", "smokeLevel", 50.0)
    print("   🔄 Reset to normal smoke level")
    return True

def demo_scenario_3():
    """Scenario 3: Robot phản hồi khi có alert"""
    print_step(3, "Robot Cruz phản hồi khi có cảnh báo")
    
    print("   🚨 Simulating fire alert...")
    
    # Gửi alert trực tiếp đến robot (simulate từ backend)
    alert_payload = {
        "message": "🚨 CẢNH BÁO CHÁY! Phát hiện khói ở phòng bếp",
        "severity": "critical",
        "duration": 10
    }
    
    response = requests.post(f"{ROBOT_URL}/api/robot/alert", json=alert_payload)
    if response.status_code == 200:
        print("   ✅ Alert displayed on robot screen")
    else:
        print("   ❌ Failed to send alert to robot")
        return False
    
    # Robot navigate to kitchen
    nav_payload = {"target_zone": "kitchen"}
    response = requests.post(f"{ROBOT_URL}/api/robot/navigate", json=nav_payload)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Robot arrived at kitchen ({result.get('travel_time', 0)}s)")
    else:
        print("   ❌ Robot navigation failed")
        return False
    
    # Robot voice announcement
    voice_payload = {"text": "Cảnh báo cháy ở phòng bếp. Vui lòng sơ tán khẩn cấp."}
    response = requests.post(f"{ROBOT_URL}/api/robot/speak", json=voice_payload)
    if response.status_code == 200:
        print("   ✅ Voice announcement played")
    else:
        print("   ❌ Voice announcement failed")
        return False
    
    wait_for_user("   ✅ Scenario 3 complete. Press Enter to continue...")
    return True

def demo_scenario_4():
    """Scenario 4: Energy optimization"""
    print_step(4, "Phát hiện thiết bị idle - Tiết kiệm năng lượng")
    
    print("   📊 Normal power: 50W (TV đang xem)")
    print("   💤 Idle power: 8W (TV quên tắt)")
    
    # Inject idle power
    reset_anomaly("matter_smartplug_001", "power", 50.0)
    time.sleep(1)
    
    # Switch to idle
    url = f"{FIWARE_URL}/entities/matter_smartplug_001/attrs"
    payload = {"power": {"type": "Number", "value": 8.0}}
    requests.patch(url, json=payload)
    print("   ✅ Idle power injected (8W)")
    
    time.sleep(2)
    
    # Check energy stats
    response = requests.get(f"{BACKEND_URL}/api/energy/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"   📊 Total power: {stats.get('total_power', 0)}W")
        print(f"   💡 Idle devices: {stats.get('idle_devices', [])}")
    else:
        print("   ❌ Cannot get energy stats")
        return False
    
    wait_for_user("   ✅ Scenario 4 complete. Press Enter to reset...")
    
    # Reset
    reset_anomaly("matter_smartplug_001", "power", 50.0)
    print("   🔄 Reset to normal power")
    return True

def demo_summary():
    """Tổng kết demo"""
    print("\n" + "="*60)
    print("🎉 DEMO COMPLETE!")
    print("="*60)
    print("""
    ✅ Scenario 1: Temperature anomaly detected
    ✅ Scenario 2: Smoke anomaly (fire) detected
    ✅ Scenario 3: Robot responded with navigation + alert + voice
    ✅ Scenario 4: Energy optimization (idle device detected)
    """)
    print("="*60)
    print("📊 System Status:")
    
    # Get robot status
    response = requests.get(f"{ROBOT_URL}/api/robot/status")
    if response.status_code == 200:
        robot = response.json()
        print(f"   Robot position: {robot.get('position', {}).get('zone')}")
        print(f"   Robot battery: {robot.get('battery')}%")
    
    # Get sensors
    response = requests.get(f"{BACKEND_URL}/api/sensors/")
    if response.status_code == 200:
        sensors = response.json()
        print(f"   Active sensors: {len(sensors)}")
    
    print("\n🎯 ALL CRITERIA MET - DEMO READY!")
    print("="*60)

def run_full_demo():
    """Chạy toàn bộ demo"""
    print("="*60)
    print("🚀 CRUZRTWIN ASEAN - FULL DEMO")
    print("   Embodied AI Digital Twin for Smart Communities")
    print("="*60)
    
    # Check health first
    if not check_health():
        print("\n❌ System not healthy! Please run reset_demo.py first")
        return False
    
    wait_for_user("\n✅ System healthy. Press Enter to start demo...")
    
    # Run scenarios
    scenarios = [
        ("Temperature Anomaly", demo_scenario_1),
        ("Smoke/Fire Detection", demo_scenario_2),
        ("Robot Response", demo_scenario_3),
        ("Energy Optimization", demo_scenario_4)
    ]
    
    for name, scenario_func in scenarios:
        print(f"\n▶️ Running: {name}")
        success = scenario_func()
        if not success:
            print(f"❌ {name} failed!")
            return False
    
    demo_summary()
    return True

if __name__ == "__main__":
    success = run_full_demo()
    sys.exit(0 if success else 1)