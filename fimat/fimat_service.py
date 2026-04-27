import time
import sys
from matter_simulator import MatterNetworkSimulator
from fiware_publisher import FIWAREPublisher
from config import FIWARE_ORION_URL, SIMULATED_DEVICES

class FIMATService:
    """Main FIMAT Service"""
    
    def __init__(self):
        self.publisher = FIWAREPublisher(FIWARE_ORION_URL)
        self.network = MatterNetworkSimulator(
            on_node_added=self.handle_node_added,
            on_attribute_updated=self.handle_attribute_updated
        )
        self.device_count = 0
        self.sync_count = 0
    
    def handle_node_added(self, node_data):
        """Xử lý sự kiện NodeAdded (thiết bị mới kết nối)"""
        device_id = node_data['device_id']
        device_type = node_data['device_type']
        
        print(f"\n[NodeAdded] {device_id} ({device_type})")
        
        # Đăng ký entity lên FIWARE
        success = self.publisher.register_entity(device_id, device_type)
        
        if success:
            self.device_count += 1
            print(f"  Total registered: {self.device_count}/{len(SIMULATED_DEVICES)}")
    
    def handle_attribute_updated(self, attr_data):
        """Xử lý sự kiện AttributeUpdated (dữ liệu cảm biến thay đổi)"""
        device_id = attr_data['device_id']
        attr_name = attr_data['attribute']
        value = attr_data['value']
        unit = attr_data.get('unit', None)
        
        # Chỉ cập nhật nếu entity đã đăng ký
        if not self.publisher.is_entity_registered(device_id):
            print(f"Skipping {device_id} - not registered yet")
            return
        
        # Cập nhật lên FIWARE
        success = self.publisher.update_attribute(device_id, attr_name, value, unit)
        
        if success:
            self.sync_count += 1
    
    def start(self):
        """Khởi động FIMAT Service"""
        print("=" * 60)
        print("  FIMAT Service Starting...")
        print(f"   FIWARE Orion: {FIWARE_ORION_URL}")
        print("=" * 60)
        
        # Thêm các thiết bị mô phỏng (giống như device connect vào mạng)
        print("\nConnecting Matter devices...")
        for device in SIMULATED_DEVICES:
            self.network.add_device(device['id'], device['type'], device.get('interval', 5))
            time.sleep(1)  # Delay giữa các device để dễ theo dõi
        
        # Bắt đầu mô phỏng dữ liệu
        print("\n  Starting data simulation...")
        self.network.start_all()
        
        print("\n   FIMAT Service Running!")
        print("   - NodeAdded: devices auto-register to FIWARE")
        print("   - AttributeUpdated: live data sync to FIWARE")
        print("\n  Press Ctrl+C to stop\n")
        
        # Print stats periodically
        try:
            while True:
                time.sleep(10)
                print(f" Stats: {self.device_count} devices | {self.sync_count} updates")
        except KeyboardInterrupt:
            print("\n\nStopping FIMAT Service...")
            self.network.stop_all()
            print("FIMAT Service stopped")
            sys.exit(0)


if __name__ == "__main__":
    service = FIMATService()
    service.start()