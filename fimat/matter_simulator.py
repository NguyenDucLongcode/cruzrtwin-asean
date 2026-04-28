import random
import time
from datetime import datetime
import threading

class MatterDeviceSimulator:
    """Mô phỏng thiết bị Matter"""
    
    def __init__(self, device_id, device_type, callback, interval=5):
        self.device_id = device_id
        self.device_type = device_type
        self.callback = callback
        self.interval = interval
        self.running = False
        self.thread = None
    
    def generate_data(self):
        """Tạo dữ liệu cảm biến mô phỏng"""
        now = datetime.now().isoformat()
        
        if self.device_type == "TemperatureSensor":
            value = round(random.uniform(22, 30), 1)
            # value = round(random.uniform(38, 45), 1)  # ← Bất thường!
            attr_name = "temperature"
            unit = "celsius"
        elif self.device_type == "HumiditySensor":
            value = round(random.uniform(45, 75), 1)
            attr_name = "humidity"
            unit = "percent"
        elif self.device_type == "SmokeSensor":
            value = round(random.uniform(20, 100), 0)
            attr_name = "smokeLevel"
            unit = "ppm"
        elif self.device_type == "AirQualitySensor":
            value = {
                "pm25": round(random.uniform(10, 50), 1),
                "pm10": round(random.uniform(20, 80), 1),
                "co2": round(random.uniform(380, 500), 0),
                "tvoc": round(random.uniform(100, 300), 0),
                "aqi": random.randint(50, 150)
            }
            attr_name = "airQuality"
            unit = None
        elif self.device_type == "SmartPlug":
            power = round(random.uniform(0, 80), 1)
            voltage = round(random.uniform(215, 225), 1)
            current = round(power / voltage, 3) if voltage else 0
            value = {
                "power": power,
                "voltage": voltage,
                "current": current,
                "energyToday": round(random.uniform(0.1, 5.0), 2),
                "onOff": random.choice([True, False])
            }
            attr_name = "smartPlug"
            unit = None
        else:
            value = 0
            attr_name = "value"
            unit = ""
        
        return {
            "event": "AttributeUpdated",
            "device_id": self.device_id,
            "device_type": self.device_type,
            "attribute": attr_name,
            "value": value,
            "unit": unit,
            "timestamp": now
        }
    
    def start(self):
        """Bắt đầu mô phỏng"""
        self.running = True
        
        def run():
            while self.running:
                data = self.generate_data()
                self.callback(data)
                time.sleep(self.interval)  # Mỗi thiết bị dùng chu kỳ riêng
        
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()
        print(f"   {self.device_id} started")
    
    def stop(self):
        """Dừng mô phỏng"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)


class MatterNetworkSimulator:
    """Mô phỏng toàn bộ mạng Matter devices"""
    
    def __init__(self, on_node_added, on_attribute_updated):
        self.devices = []
        self.on_node_added = on_node_added
        self.on_attribute_updated = on_attribute_updated
    
    def add_device(self, device_id, device_type, interval=5):
        """Thêm thiết bị mới (NodeAdded event)"""
        device = MatterDeviceSimulator(device_id, device_type, self._handle_data, interval=interval)
        self.devices.append(device)
        
        # Fire NodeAdded event
        self.on_node_added({
            "event": "NodeAdded",
            "device_id": device_id,
            "device_type": device_type,
            "timestamp": datetime.now().isoformat()
        })
        
        return device
    
    def _handle_data(self, data):
        """Xử lý data từ device (AttributeUpdated event)"""
        self.on_attribute_updated(data)
    
    def start_all(self):
        """Khởi động tất cả device"""
        for device in self.devices:
            device.start()
    
    def stop_all(self):
        """Dừng tất cả device"""
        for device in self.devices:
            device.stop()


# Test
if __name__ == "__main__":
    def on_node_added(node):
        print(f"  NodeAdded: {node['device_id']} ({node['device_type']})")
    
    def on_attribute_updated(attr):
        print(f"  AttributeUpdated: {attr['device_id']} = {attr['value']}")
    
    network = MatterNetworkSimulator(on_node_added, on_attribute_updated)
    
    network.add_device("matter_temp_001", "TemperatureSensor")
    network.add_device("matter_humid_001", "HumiditySensor")
    network.add_device("matter_smoke_001", "SmokeSensor")
    
    network.start_all()
    
    print("\nMatter network simulator running... Press Ctrl+C to stop\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        network.stop_all()