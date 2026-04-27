"""
T-22: Backup Plan
Phương án dự phòng nếu demo chính fail
"""

import requests
import time

def backup_demo():
    """Demo rút gọn nếu có lỗi"""
    print("\n" + "="*60)
    print("🔄 BACKUP DEMO MODE")
    print("   (Fallback if main demo fails)")
    print("="*60)
    
    # Kiểm tra services nào đang chạy
    services_status = {}
    
    # Check Backend
    try:
        r = requests.get("http://localhost:8000/health", timeout=2)
        services_status['backend'] = r.status_code == 200
    except:
        services_status['backend'] = False
    
    # Check Robot
    try:
        r = requests.get("http://localhost:8001/health", timeout=2)
        services_status['robot'] = r.status_code == 200
    except:
        services_status['robot'] = False
    
    # Check FIWARE
    try:
        r = requests.get("http://localhost:1026/version", timeout=2)
        services_status['fiware'] = r.status_code == 200
    except:
        services_status['fiware'] = False
    
    print("\n📊 Services Status:")
    for service, status in services_status.items():
        print(f"   {service}: {'✅' if status else '❌'}")
    
    # Demo với services đang chạy
    print("\n🎬 Simplified Demo:")
    
    if services_status['robot']:
        print("   1. Robot navigation test:")
        try:
            r = requests.post("http://localhost:8001/api/robot/navigate", 
                              json={"target_zone": "demo_zone"})
            if r.status_code == 200:
                print("      ✅ Robot can navigate")
        except:
            print("      ⚠️ Robot navigation failed")
        
        print("   2. Robot alert test:")
        try:
            r = requests.post("http://localhost:8001/api/robot/alert",
                              json={"message": "Demo alert", "severity": "info"})
            if r.status_code == 200:
                print("      ✅ Alert display works")
        except:
            print("      ⚠️ Alert display failed")
    
    if services_status['backend']:
        print("   3. Backend API test:")
        try:
            r = requests.get("http://localhost:8000/health")
            if r.status_code == 200:
                print("      ✅ Backend API works")
        except:
            print("      ⚠️ Backend API failed")
    
    print("\n" + "="*60)
    print("📋 Backup Demo Instructions:")
    print("   1. Show video recording of full demo")
    print("   2. Explain architecture via slides")
    print("   3. Show screenshots of dashboard")
    print("   4. Demonstrate code on GitHub")
    print("="*60)

if __name__ == "__main__":
    backup_demo()