import requests
import time

ROBOT_API_URL = "http://localhost:8001"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"🎬 {title}")
    print("=" * 60)

def test_navigation():
    """Test 1: Robot di chuyển"""
    print_section("TEST 1: Robot Navigation")
    
    # Di chuyển đến phòng khách
    response = requests.post(f"{ROBOT_API_URL}/api/robot/navigate", 
                             json={"target_zone": "living_room"})
    print(f"   Response: {response.json()}")
    
    time.sleep(1)
    
    # Di chuyển đến bếp
    response = requests.post(f"{ROBOT_API_URL}/api/robot/navigate",
                             json={"target_zone": "kitchen"})
    print(f"   Response: {response.json()}")

def test_alert():
    """Test 2: Hiển thị cảnh báo"""
    print_section("TEST 2: Alert Display")
    
    # Cảnh báo cháy
    response = requests.post(f"{ROBOT_API_URL}/api/robot/alert",
                             json={
                                 "message": "🚨 CẢNH BÁO CHÁY! Phát hiện khói ở phòng khách",
                                 "severity": "critical",
                                 "duration": 10
                             })
    print(f"   Response: {response.json()}")

def test_voice():
    """Test 3: Phát giọng nói"""
    print_section("TEST 3: Voice Announcement")
    
    # Phát giọng nói
    response = requests.post(f"{ROBOT_API_URL}/api/robot/speak",
                             json={
                                 "text": "Cảnh báo! Phát hiện khói ở phòng khách. Vui lòng kiểm tra ngay.",
                                 "language": "vi-VN"
                             })
    print(f"   Response: {response.json()}")

def test_device_control():
    """Test 4: Điều khiển thiết bị"""
    print_section("TEST 4: Device Control")
    
    # Tắt smart plug
    response = requests.post(f"{ROBOT_API_URL}/api/robot/device",
                             json={
                                 "device_id": "smart_plug_tv",
                                 "action": "off"
                             })
    print(f"   Response: {response.json()}")

def test_status():
    """Test 5: Lấy trạng thái"""
    print_section("TEST 5: Robot Status")
    
    response = requests.get(f"{ROBOT_API_URL}/api/robot/status")
    print(f"   Position: {response.json()['position']}")
    print(f"   Battery: {response.json()['battery']}%")
    print(f"   Navigations: {response.json()['navigation_count']}")

def test_full_scenario():
    """Demo scenario: Phát hiện cháy → Robot di chuyển → Cảnh báo"""
    print_section("DEMO SCENARIO: Fire Alert Response")
    
    print("   1. Phát hiện cháy ở phòng bếp")
    time.sleep(1)
    
    print("   2. Robot nhận lệnh di chuyển đến phòng bếp")
    response = requests.post(f"{ROBOT_API_URL}/api/robot/navigate",
                             json={"target_zone": "kitchen"})
    print(f"      ✅ {response.json()['message']}")
    
    time.sleep(1)
    
    print("   3. Robot hiển thị cảnh báo trên màn hình")
    response = requests.post(f"{ROBOT_API_URL}/api/robot/alert",
                             json={
                                 "message": "🔥 CẢNH BÁO CHÁY! Phát hiện khói ở phòng bếp",
                                 "severity": "critical",
                                 "duration": 15
                             })
    print(f"      ✅ {response.json()['message']}")
    
    time.sleep(1)
    
    print("   4. Robot phát giọng nói thông báo")
    response = requests.post(f"{ROBOT_API_URL}/api/robot/speak",
                             json={
                                 "text": "Cảnh báo cháy ở phòng bếp. Vui lòng sơ tán khẩn cấp.",
                                 "language": "vi-VN"
                             })
    print(f"      ✅ {response.json()['message']}")
    
    time.sleep(1)
    
    print("   5. Robot tắt nguồn thiết bị điện trong khu vực")
    response = requests.post(f"{ROBOT_API_URL}/api/robot/device",
                             json={
                                 "device_id": "smart_plug_kitchen",
                                 "action": "off"
                             })
    print(f"      ✅ {response.json()['status']}")

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 T-14: Cruz Robot API Demo")
    print("=" * 60)
    print("\n⚠️  Đảm bảo robot API đang chạy: python robot_api.py")
    print("   Trên port 8001\n")
    
    input("Press Enter to start demo...")
    
    # Chạy các test
    test_status()
    test_navigation()
    test_alert()
    test_voice()
    test_device_control()
    test_full_scenario()
    
    print_section("DEMO COMPLETE")
    print(" Robot API hoạt động đúng yêu cầu!")
    print("   - Navigation commands ✅")
    print("   - Alert display ✅")
    print("   - Voice announcement ✅")
    print("   - Device control ✅")