"""Debug script để kiểm tra kết nối FIWARE Orion"""
import requests
import json
from datetime import datetime

FIWARE_ORION_URL = "http://localhost:1026/v2"

def check_connection():
    """Kiểm tra FIWARE Orion có chạy không"""
    print("=" * 60)
    print(" FIWARE Orion Connection Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{FIWARE_ORION_URL}/entities", timeout=5)
        print(f"\n FIWARE Orion is RUNNING")
        print(f"   URL: {FIWARE_ORION_URL}")
        print(f"   Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"\n FIWARE Orion NOT RUNNING")
        print(f"   Cannot connect to: {FIWARE_ORION_URL}")
        print(f"\n   Start it with:")
        print(f"   docker-compose -f fiware/docker-compose.yml up -d")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def list_entities():
    """Liệt kê tất cả entities hiện tại"""
    print("\n" + "=" * 60)
    print(" Current Entities in FIWARE")
    print("=" * 60)
    
    try:
        response = requests.get(f"{FIWARE_ORION_URL}/entities")
        if response.status_code == 200:
            entities = response.json()
            if entities:
                print(f"\nFound {len(entities)} entities:")
                for entity in entities:
                    print(f"  - {entity['id']} (type: {entity['type']})")
            else:
                print("\n No entities found")
            return True
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_create_entity():
    """Test tạo một entity mới"""
    print("\n" + "=" * 60)
    print(" Test Creating Entity")
    print("=" * 60)
    
    test_entity = {
        "id": "test_sensor_debug",
        "type": "TestSensor",
        "value": {"type": "Number", "value": 25.0},
        "TimeInstant": {"type": "DateTime", "value": datetime.now().isoformat()}
    }
    
    print(f"\nPayload:")
    print(json.dumps(test_entity, indent=2))
    
    try:
        # Delete if exists
        print("\n1️ Delete if exists...")
        del_response = requests.delete(
            f"{FIWARE_ORION_URL}/entities/test_sensor_debug",
            timeout=5
        )
        print(f"   DELETE status: {del_response.status_code}")
        
        # Create new
        print("\n2️  Creating new entity...")
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{FIWARE_ORION_URL}/entities",
            json=test_entity,
            headers=headers,
            timeout=5
        )
        print(f"   POST status: {response.status_code}")
        if response.status_code >= 400:
            print(f"   Error: {response.text}")
            return False
        
        # Verify creation
        print("\n3️  Verifying creation...")
        verify_response = requests.get(
            f"{FIWARE_ORION_URL}/entities/test_sensor_debug",
            timeout=5
        )
        print(f"   GET status: {verify_response.status_code}")
        if verify_response.status_code == 200:
            entity = verify_response.json()
            print(f"   Entity created successfully!")
            print(f"   Value: {entity.get('value', {}).get('value')}")
            
            # Clean up
            print("\n4️ Cleanup...")
            cleanup_response = requests.delete(
                f"{FIWARE_ORION_URL}/entities/test_sensor_debug",
                timeout=5
            )
            print(f"   DELETE status: {cleanup_response.status_code}")
            return True
        else:
            print(f"    Error: {verify_response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Check connection first
    if not check_connection():
        print("\n Cannot proceed without FIWARE Orion")
        exit(1)
    
    # List current entities
    list_entities()
    
    # Test create entity
    test_create_entity()
    
    print("\n" + "=" * 60)
    print(" Check complete")
    print("=" * 60)
