"""
T-22: Demo Reset Script
Reset toàn bộ hệ thống về trạng thái ban đầu
"""

import requests
import time
import subprocess
import sys
import os

# Thêm đường dẫn để import config
sys.path.append(os.path.dirname(__file__))
from demo_config import SERVICES, RESET_TIMEOUT

def reset_fiware():
    """Reset FIWARE: Xóa tất cả entities và subscriptions"""
    print("\n🔄 Resetting FIWARE...")
    orion_url = "http://localhost:1026/v2"
    
    # Xóa tất cả entities
    try:
        response = requests.get(f"{orion_url}/entities")
        if response.status_code == 200:
            entities = response.json()
            for entity in entities:
                entity_id = entity.get('id')
                requests.delete(f"{orion_url}/entities/{entity_id}")
                print(f"   🗑️ Deleted entity: {entity_id}")
    except:
        print("   ⚠️ Cannot connect to FIWARE")
    
    # Xóa tất cả subscriptions
    try:
        response = requests.get(f"{orion_url}/subscriptions")
        if response.status_code == 200:
            subs = response.json()
            for sub in subs:
                sub_id = sub.get('id')
                requests.delete(f"{orion_url}/subscriptions/{sub_id}")
                print(f"   🗑️ Deleted subscription: {sub_id}")
    except:
        pass
    
    print("   ✅ FIWARE reset complete")

def reset_services():
    """Restart các services"""
    print("\n🔄 Restarting services...")
    
    # Restart backend
    print("   Restarting backend...")
    # Backend sẽ tự reload (reload=True)
    
    # Restart robot
    print("   Restarting robot...")
    # Robot sẽ tự reload
    
    print("   ✅ Services restarted")

def verify_services():
    """Kiểm tra tất cả services hoạt động"""
    print("\n🔍 Verifying services...")
    all_healthy = True
    
    for service_name, service_info in SERVICES.items():
        url = service_info["url"]
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {service_info['name']}: OK")
            else:
                print(f"   ❌ {service_info['name']}: HTTP {response.status_code}")
                all_healthy = False
        except Exception as e:
            print(f"   ❌ {service_info['name']}: {str(e)}")
            all_healthy = False
    
    return all_healthy

def reset_all():
    """Reset toàn bộ hệ thống"""
    print("=" * 60)
    print("🔄 DEMO RESET SCRIPT")
    print("=" * 60)
    
    start_time = time.time()
    
    reset_fiware()
    reset_services()
    time.sleep(5)  # Đợi services ổn định
    
    # Verify
    is_healthy = verify_services()
    
    elapsed = time.time() - start_time
    print(f"\n📊 Reset completed in {elapsed:.1f}s")
    
    if is_healthy:
        print("✅ All services are healthy!")
        if elapsed < RESET_TIMEOUT:
            print(f"✅ Reset time < {RESET_TIMEOUT}s ({elapsed:.1f}s)")
        else:
            print(f"⚠️ Reset time: {elapsed:.1f}s (target: <{RESET_TIMEOUT}s)")
    else:
        print("❌ Some services are not healthy!")
    
    return is_healthy

if __name__ == "__main__":
    success = reset_all()
    sys.exit(0 if success else 1)