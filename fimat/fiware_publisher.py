# fimat/fiware_publisher.py
import requests
import time
from datetime import datetime

class FIWAREPublisher:
    """Gửi dữ liệu từ Matter lên FIWARE Orion"""
    
    def __init__(self, orion_url="http://localhost:1026/v2"):
        self.orion_url = orion_url
        self.registered_entities = {}
    
    def register_entity(self, device_id, device_type, initial_data=None):
        """
        Đăng ký entity mới lên Orion (khi NodeAdded)
        Yêu cầu latency < 500ms
        """
        start_time = time.time()
        
        # Khởi tạo entity với các attribute mặc định theo từng loại
        entity = {
            "id": device_id,
            "type": device_type,
            "TimeInstant": {
                "type": "DateTime",
                "value": datetime.now().isoformat(),
                "metadata": {}
            }
        }
        
        # Thêm attribute mặc định cho từng loại sensor
        if device_type == "TemperatureSensor":
            entity["temperature"] = {"type": "Number", "value": 0, "metadata": {"unit": {"value": "celsius"}}}
            entity["battery"] = {"type": "Number", "value": 100, "metadata": {"unit": {"value": "percent"}}}
            entity["status"] = {"type": "Text", "value": "online", "metadata": {}}
        elif device_type == "HumiditySensor":
            entity["humidity"] = {"type": "Number", "value": 0, "metadata": {"unit": {"value": "percent"}}}
            entity["battery"] = {"type": "Number", "value": 100, "metadata": {"unit": {"value": "percent"}}}
            entity["status"] = {"type": "Text", "value": "online", "metadata": {}}
        elif device_type == "SmokeSensor":
            entity["smokeLevel"] = {"type": "Number", "value": 0, "metadata": {"unit": {"value": "ppm"}}}
            entity["alarm"] = {"type": "Boolean", "value": False, "metadata": {}}
            entity["battery"] = {"type": "Number", "value": 100, "metadata": {"unit": {"value": "percent"}}}
            entity["status"] = {"type": "Text", "value": "online", "metadata": {}}
        elif device_type == "AirQualitySensor":
            entity["pm25"] = {"type": "Number", "value": 0, "metadata": {"unit": {"value": "ugm3"}}}
            entity["pm10"] = {"type": "Number", "value": 0, "metadata": {"unit": {"value": "ugm3"}}}
            entity["co2"] = {"type": "Number", "value": 0, "metadata": {"unit": {"value": "ppm"}}}
            entity["tvoc"] = {"type": "Number", "value": 0, "metadata": {"unit": {"value": "ppb"}}}
            entity["aqi"] = {"type": "Integer", "value": 0, "metadata": {}}
            entity["battery"] = {"type": "Number", "value": 100, "metadata": {"unit": {"value": "percent"}}}
            entity["status"] = {"type": "Text", "value": "online", "metadata": {}}
        elif device_type == "SmartPlug":
            entity["power"] = {"type": "Number", "value": 0, "metadata": {"unit": {"value": "watt"}}}
            entity["voltage"] = {"type": "Number", "value": 0, "metadata": {"unit": {"value": "volt"}}}
            entity["current"] = {"type": "Number", "value": 0, "metadata": {"unit": {"value": "ampere"}}}
            entity["energyToday"] = {"type": "Number", "value": 0, "metadata": {"unit": {"value": "kwh"}}}
            entity["onOff"] = {"type": "Boolean", "value": False, "metadata": {}}
            entity["status"] = {"type": "Text", "value": "online", "metadata": {}}
        
        url = f"{self.orion_url}/entities"
        headers = {"Content-Type": "application/json"}
        
        # Xóa entity cũ nếu tồn tại
        requests.delete(f"{self.orion_url}/entities/{device_id}")
        
        response = requests.post(url, headers=headers, json=entity)
        
        latency = (time.time() - start_time) * 1000
        
        if response.status_code in [201, 204]:
            self.registered_entities[device_id] = device_type
            print(f"   Registered: {device_id} ({latency:.1f}ms)")
            return True
        else:
            print(f"   Failed: {device_id} - {response.status_code}")
            print(f"      Response: {response.text}")
            return False
    
    def update_attribute(self, device_id, attr_name, value, unit=None):
        """Cập nhật attribute của entity (khi AttributeUpdated)"""
        start_time = time.time()
        
        url = f"{self.orion_url}/entities/{device_id}/attrs"
        headers = {"Content-Type": "application/json"}
        
        # Xử lý value cho đúng format
        if isinstance(value, (int, float)):
            payload = {
                attr_name: {
                    "type": "Number",
                    "value": value
                }
            }
            if unit:
                payload[attr_name]["metadata"] = {"unit": {"value": unit}}
            response = requests.patch(url, headers=headers, json=payload)
        
        elif isinstance(value, dict):
            # Dict type (cho air quality và smart plug)
            payload = {}
            unit_map = {
                "temperature": "celsius",
                "humidity": "percent",
                "smokeLevel": "ppm",
                "pm25": "ugm3",
                "pm10": "ugm3",
                "co2": "ppm",
                "tvoc": "ppb",
                "power": "watt",
                "voltage": "volt",
                "current": "ampere",
                "energyToday": "kwh",
                "battery": "percent",
            }
            for k, v in value.items():
                if isinstance(v, bool):
                    attr_type = "Boolean"
                elif k == "aqi":
                    attr_type = "Integer"
                elif isinstance(v, (int, float)):
                    attr_type = "Number"
                else:
                    attr_type = "Text"
                payload[k] = {
                    "type": attr_type,
                    "value": v
                }
                if k in unit_map:
                    payload[k]["metadata"] = {"unit": {"value": unit_map[k]}}
            response = requests.patch(url, headers=headers, json=payload)
        else:
            payload = {
                attr_name: {
                    "type": "Text",
                    "value": str(value)
                }
            }
            response = requests.patch(url, headers=headers, json=payload)
        
        latency = (time.time() - start_time) * 1000
        
        if response.status_code == 204:
            print(f"   Updated: {device_id}.{attr_name} = {value} ({latency:.1f}ms)")
            return True
        else:
            print(f"   Update failed: {device_id} - {response.status_code}")
            print(f"      Response: {response.text}")
            return False
    
    def is_entity_registered(self, device_id):
        return device_id in self.registered_entities


# Test
if __name__ == "__main__":
    print("Testing FIWARE Publisher...")
    publisher = FIWAREPublisher()
    
    # Test register
    publisher.register_entity("test_sensor_001", "TemperatureSensor", {"temperature": 25.5})
    
    # Test update
    publisher.update_attribute("test_sensor_001", "temperature", 26.5, "celsius")
    
    # Cleanup
    requests.delete("http://localhost:1026/v2/entities/test_sensor_001")