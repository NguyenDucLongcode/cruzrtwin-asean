import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

class Low_Power_Idle:
    def __init__(self, model_path='anomaly_model.pkl', no_person_timeout_minutes=20):
        """
        Khởi tạo Energy Optimizer - Tích hợp model T-07 để phát hiện bất thường năng lượng
        
        Args:
            model_path: Đường dẫn đến model anomaly detection
            no_person_timeout_minutes: Thời gian không phát hiện người (phút) trước khi đề xuất tắt
        """
        resolved_model_path = self._resolve_model_path(model_path)
        self.model = joblib.load(resolved_model_path)
        self.model_path = resolved_model_path
        self.no_person_timeout_minutes = no_person_timeout_minutes  # 20 phút mặc định
        
        self.idle_power_threshold = 10.0   # Watts - fallback nếu không nhận diện được loại thiết bị
        self.idle_time_threshold = 30      # phút - fallback nếu không nhận diện được loại thiết bị
        self.confirmation_readings = 3     # cần ít nhất N mẫu liên tiếp dưới ngưỡng

        # Cấu hình thực tế theo loại thiết bị (dựa trên device_id)
        self.device_profiles = {
            'tv': {'idle_power_threshold': 12.0, 'idle_time_threshold': 20},
            'fan': {'idle_power_threshold': 9.0, 'idle_time_threshold': 45},
            'light': {'idle_power_threshold': 5.0, 'idle_time_threshold': 15},
            'default': {'idle_power_threshold': self.idle_power_threshold, 'idle_time_threshold': self.idle_time_threshold}
        }

        self.device_history = {}           # Lưu lịch sử từng thiết bị
        self.motion_history = {            # Lưu lịch sử cảm biến chuyển động
            'last_motion_time': None,
            'last_motion_device_id': None,
            'motion_log': []               # Lưu log phát hiện chuyển động gần đây
        }
        
        print("=" * 60)
        print("AI ENERGY OPTIMIZATION MODULE (T-10)")
        print(f"   - Model T-07 loaded: {self.model_path}")
        print(f"   - Idle threshold: {self.idle_power_threshold}W trong {self.idle_time_threshold} phút")
        print(f"   - No-person timeout: {self.no_person_timeout_minutes} phút")
        print(f"   - Confirmation readings: {self.confirmation_readings}")
        print("=" * 60)

    def _normalize_timestamp(self, timestamp):
        """Chuẩn hóa timestamp về datetime, tránh crash khi dữ liệu bị lỗi format."""
        if isinstance(timestamp, datetime):
            return timestamp
        if isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp)
            except ValueError:
                return None
        return None

    def _get_device_profile(self, device_id):
        """Map device_id sang profile thực tế, không match thì dùng default."""
        normalized = str(device_id).lower()
        for key in ('tv', 'fan', 'light'):
            if key in normalized:
                return self.device_profiles[key]
        return self.device_profiles['default']

    def _resolve_model_path(self, model_path):
        """Tự tìm vị trí model theo nhiều path phổ biến trong project."""
        base_dir = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))

        candidates = []

        # Ưu tiên path người dùng truyền vào.
        if os.path.isabs(model_path):
            candidates.append(model_path)
        else:
            candidates.append(os.path.join(base_dir, model_path))
            candidates.append(os.path.join(project_root, model_path))

        # Fallback path chuẩn của repo.
        candidates.append(os.path.join(project_root, "ai-models", "training", "models", "anomaly_model.pkl"))
        candidates.append(os.path.join(project_root, "anomaly_model.pkl"))

        for candidate in candidates:
            normalized = os.path.abspath(candidate)
            if os.path.exists(normalized):
                return normalized

        searched_paths = "\n".join(f"- {os.path.abspath(path)}" for path in candidates)
        raise FileNotFoundError(
            "Không tìm thấy file model anomaly_model.pkl. Đã kiểm tra các path:\n"
            f"{searched_paths}\n"
            "Hãy chạy: python ai-models/training/train_anomaly_model.py"
        )
    
    def update_motion_sensor(self, device_data):
        """
        Cập nhật trạng thái từ cảm biến chuyển động
        
        Args:
            device_data: list of dict với các keys: device_id, motion_detected, timestamp
        """
        for sensor in device_data:
            # Kiểm tra nếu là cảm biến chuyển động (PIR sensor)
            device_id = sensor.get('device_id', '').lower()
            if 'motion' in device_id or 'pir' in device_id or 'movement' in device_id:
                motion_detected = sensor.get('motion_detected', False)
                timestamp = self._normalize_timestamp(sensor.get('timestamp'))
                
                if timestamp is None:
                    continue
                
                if motion_detected:
                    self.motion_history['last_motion_time'] = timestamp
                    self.motion_history['last_motion_device_id'] = sensor.get('device_id')
                    self.motion_history['motion_log'].append({
                        'time': timestamp,
                        'device_id': sensor.get('device_id'),
                        'motion_detected': True
                    })
                    
                    # Giữ 100 log gần nhất
                    if len(self.motion_history['motion_log']) > 100:
                        self.motion_history['motion_log'].pop(0)
    
    def is_person_present(self, current_time=None):
        """
        Kiểm tra có người trong phòng không dựa trên cảm biến chuyển động
        
        Returns:
            tuple: (is_present, minutes_since_last_motion)
        """
        if current_time is None:
            current_time = datetime.now()
        
        if self.motion_history['last_motion_time'] is None:
            # Chưa có dữ liệu cảm biến, mặc định coi như có người (để an toàn)
            return True, 0
        
        minutes_since_last = (current_time - self.motion_history['last_motion_time']).total_seconds() / 60
        
        # Có người nếu phát hiện chuyển động trong khoảng timeout
        is_present = minutes_since_last <= self.no_person_timeout_minutes
        
        return is_present, minutes_since_last
    
    def detect_idle_devices(self, device_data):
        """
        Phát hiện thiết bị idle (bật nhưng không dùng)
        
        Args:
            device_data: list of dict với các keys: device_id, power, onOff, timestamp
        
        Returns:
            list: danh sách thiết bị idle cần xử lý
        """
        # Cập nhật cảm biến chuyển động
        self.update_motion_sensor(device_data)
        
        # Kiểm tra trạng thái có người
        current_time = datetime.now()
        is_person_present, minutes_since_motion = self.is_person_present(current_time)
        
        idle_devices = []
        
        for device in device_data:
            device_id = device.get('device_id')
            power = device.get('power')
            is_on = device.get('onOff', False)
            timestamp = self._normalize_timestamp(device.get('timestamp'))
            
            # Bỏ qua nếu là cảm biến chuyển động (không phải thiết bị điện)
            device_id_lower = str(device_id).lower()
            if 'motion' in device_id_lower or 'pir' in device_id_lower or 'movement' in device_id_lower:
                continue

            # Bỏ qua sample lỗi để tăng độ chịu lỗi telemetry
            if device_id is None or power is None or timestamp is None:
                continue

            profile = self._get_device_profile(device_id)
            power_threshold = profile['idle_power_threshold']
            time_threshold = profile['idle_time_threshold']
            
            # Chỉ xét thiết bị đang BẬT
            if not is_on:
                continue
            
            # Khởi tạo lịch sử nếu thiết bị mới
            if device_id not in self.device_history:
                self.device_history[device_id] = {
                    'idle_start_time': None,
                    'last_active_time': timestamp,
                    'below_threshold_count': 0,
                    'shutdown_recommended': False,
                    'readings': []
                }
            
            # Cập nhật readings
            self.device_history[device_id]['readings'].append({
                'time': timestamp,
                'power': power
            })
            
            # Giữ 50 readings gần nhất
            if len(self.device_history[device_id]['readings']) > 50:
                self.device_history[device_id]['readings'].pop(0)
            
            # Kiểm tra idle
            if power < power_threshold:
                # Bắt đầu tính idle
                if self.device_history[device_id]['idle_start_time'] is None:
                    self.device_history[device_id]['idle_start_time'] = timestamp

                self.device_history[device_id]['below_threshold_count'] += 1
                
                # Tính thời gian idle
                idle_duration = (timestamp - self.device_history[device_id]['idle_start_time']).total_seconds() / 60
                
                # Dùng ML từ T-07 để xác nhận (optional)
                ml_anomaly = self._check_anomaly_with_ml(power)
                
                # KIỂM TRA THÊM ĐIỀU KIỆN: KHÔNG CÓ NGƯỜI
                no_person_condition = not is_person_present
                
                if (
                    idle_duration >= time_threshold
                    and self.device_history[device_id]['below_threshold_count'] >= self.confirmation_readings
                    and not self.device_history[device_id]['shutdown_recommended']
                    and no_person_condition  # CHỈ KHUYẾN NGHỊ TẮT KHI KHÔNG CÓ NGƯỜI
                ):
                    power_saving = power * 24 / 1000  # kWh/ngày ước tính
                    
                    idle_devices.append({
                        'device_id': device_id,
                        'idle_duration_minutes': round(idle_duration, 1),
                        'current_power': round(power, 1),
                        'threshold_power': power_threshold,
                        'threshold_time_minutes': time_threshold,
                        'ml_confirmed': ml_anomaly,
                        'minutes_since_motion': round(minutes_since_motion, 1),
                        'no_person_timeout': self.no_person_timeout_minutes,
                        'action': 'recommend_shutdown',
                        'recommendation': (
                            f"[TIẾT KIỆM] Tắt {device_id} - "
                            f"idle {idle_duration:.0f} phút (ngưỡng {time_threshold} phút), "
                            f"công suất {power:.1f}W (ngưỡng {power_threshold}W), "
                            f"không phát hiện người {minutes_since_motion:.0f} phút (ngưỡng {self.no_person_timeout_minutes} phút)"
                        )
                    })
                    # Chỉ gửi 1 khuyến nghị cho 1 phiên idle để tránh spam command.
                    self.device_history[device_id]['shutdown_recommended'] = True
                    
            else:
                # Thiết bị đang hoạt động -> reset idle
                self.device_history[device_id]['idle_start_time'] = None
                self.device_history[device_id]['last_active_time'] = timestamp
                self.device_history[device_id]['below_threshold_count'] = 0
                self.device_history[device_id]['shutdown_recommended'] = False
        
        # Thêm thông tin về trạng thái có người vào kết quả để debug
        self._last_person_status = {
            'is_person_present': is_person_present,
            'minutes_since_motion': minutes_since_motion,
            'last_motion_time': self.motion_history['last_motion_time']
        }
        
        return idle_devices
    
    def _check_anomaly_with_ml(self, power):
        """Dùng model từ T-07 để kiểm tra bất thường về năng lượng"""
        # Tạo features giả lập (vì model cần 5 features)
        # Nhiệt độ, độ ẩm, khói, CO2 được giả định bình thường
        features = pd.DataFrame([[25, 60, 50, 400, power]], 
                                columns=['temperature', 'humidity', 'smoke', 'co2', 'power'])
        pred = self.model.predict(features)[0]
        return pred == -1  # -1 là bất thường
    
    def generate_fiware_command(self, device_id, action='off'):
        """
        Tạo FIWARE command để điều khiển smart plug
        
        Args:
            device_id: ID của thiết bị (entity id trong FIWARE)
            action: 'off' hoặc 'on'
        
        Returns:
            dict: FIWARE NGSI-v2 command format
        """
        command = {
            "command": "toggle_smart_plug",
            "device_id": device_id,
            "action": action,
            "payload": {
                "onOff": {
                    "type": "Boolean",
                    "value": False if action == 'off' else True
                }
            },
            "source": "T-10_Energy_Optimizer",
            "timestamp": datetime.now().isoformat()
        }
        
        if action == 'off':
            command["reason"] = "energy_optimization_idle_detection_and_no_person"
        
        return command
    
    def process_and_recommend(self, device_data):
        """
        Xử lý dữ liệu và trả về khuyến nghị + FIWARE commands
        
        Returns:
            dict: Kết quả phân tích
        """
        idle_devices = self.detect_idle_devices(device_data)
        
        # Lọc chỉ giữ các thiết bị idle thực sự (có ngưỡng thời gian)
        confirmed_idle = [d for d in idle_devices if d.get('action') == 'recommend_shutdown']
        
        # Tính số kWh tiết kiệm dự kiến (giả sử mỗi thiết bị 100W)
        estimated_savings_kwh = len(confirmed_idle) * 0.1 * 24  # 100W * 24h
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'person_status': {
                'is_person_present': self._last_person_status['is_person_present'],
                'minutes_since_last_motion': round(self._last_person_status['minutes_since_motion'], 1),
                'last_motion_time': self._last_person_status['last_motion_time'].isoformat() if self._last_person_status['last_motion_time'] else None,
                'no_person_timeout_minutes': self.no_person_timeout_minutes
            },
            'total_devices_analyzed': len([d for d in device_data if d.get('onOff', False) and 'motion' not in str(d.get('device_id', '')).lower()]),
            'idle_devices_found': len(confirmed_idle),
            'estimated_daily_savings_kwh': round(estimated_savings_kwh, 2),
            'recommendations': [],
            'fiware_commands': []
        }
        
        for device in confirmed_idle:
            result['recommendations'].append(device['recommendation'])
            result['fiware_commands'].append(
                self.generate_fiware_command(device['device_id'], 'off')
            )
        
        return result
    
    def get_motion_statistics(self):
        """
        Lấy thống kê về cảm biến chuyển động
        
        Returns:
            dict: Thống kê motion sensor
        """
        return {
            'last_motion_time': self.motion_history['last_motion_time'],
            'last_motion_device': self.motion_history['last_motion_device_id'],
            'total_motion_events': len(self.motion_history['motion_log']),
            'recent_motion_log': self.motion_history['motion_log'][-10:]  # 10 sự kiện gần nhất
        }


# ================== TEST MODULE ==================
if __name__ == "__main__":
    print("\nTESTING ENERGY OPTIMIZER MODULE WITH MOTION SENSOR\n")
    
    optimizer = Low_Power_Idle(no_person_timeout_minutes=20)
    
    # Tạo dữ liệu mô phỏng
    now = datetime.now()
    motion_time = now - timedelta(minutes=25)  # 25 phút trước có người
    
    test_data = [
        # Cảm biến chuyển động (PIR sensor)
        {'device_id': 'motion_sensor_livingroom', 'motion_detected': True, 'timestamp': motion_time},
        {'device_id': 'motion_sensor_livingroom', 'motion_detected': False, 'timestamp': motion_time + timedelta(seconds=5)},
        
        # Cảm biến chuyển động khác trong phòng
        {'device_id': 'pir_sensor_hall', 'motion_detected': False, 'timestamp': now - timedelta(minutes=30)},
        
        # TV: idle 45 phút, công suất thấp (cần tắt vì không có người)
        {'device_id': 'smart_plug_tv', 'power': 8.2, 'onOff': True, 'timestamp': now - timedelta(minutes=45)},
        {'device_id': 'smart_plug_tv', 'power': 8.1, 'onOff': True, 'timestamp': now - timedelta(minutes=30)},
        {'device_id': 'smart_plug_tv', 'power': 7.9, 'onOff': True, 'timestamp': now},
        
        # Quạt: đang chạy bình thường (không idle)
        {'device_id': 'smart_plug_fan', 'power': 45.0, 'onOff': True, 'timestamp': now},
        
        # Đèn: đã tắt (không xét)
        {'device_id': 'smart_plug_light', 'power': 0, 'onOff': False, 'timestamp': now},
        
        # Điều hòa: công suất thấp nhưng được dùng khi có người
        {'device_id': 'smart_plug_ac', 'power': 850.0, 'onOff': True, 'timestamp': now},
    ]
    
    result = optimizer.process_and_recommend(test_data)
    
    print("\nKẾT QUẢ PHÂN TÍCH:")
    print(f"   Trạng thái có người: {'CÓ' if result['person_status']['is_person_present'] else 'KHÔNG'}")
    print(f"   Phút từ lần cuối có motion: {result['person_status']['minutes_since_last_motion']} phút")
    print(f"   Ngưỡng không người: {result['person_status']['no_person_timeout_minutes']} phút")
    print(f"   Thiết bị đang bật: {result['total_devices_analyzed']}")
    print(f"   Idle devices: {result['idle_devices_found']}")
    print(f"   Tiết kiệm dự kiến: {result['estimated_daily_savings_kwh']:.2f} kWh/ngày")
    
    print("\nKHUYẾN NGHỊ:")
    for rec in result['recommendations']:
        print(f"   → {rec}")
    
    if not result['recommendations']:
        print("   → Không có khuyến nghị tắt thiết bị (có người trong phòng hoặc thiết bị đang hoạt động)")
    
    print("\nFIWARE COMMANDS (để toggle smart plug):")
    for cmd in result['fiware_commands']:
        print(f"   → {cmd}")
    
    print("\nTHỐNG KÊ MOTION SENSOR:")
    stats = optimizer.get_motion_statistics()
    print(f"   Lần cuối phát hiện motion: {stats['last_motion_time']}")
    print(f"   Tổng số sự kiện motion: {stats['total_motion_events']}")
    
    print("\n=== TEST TRƯỜNG HỢP CÓ NGƯỜI (MOTION GẦN ĐÂY) ===")
    # Reset và test với motion gần đây
    optimizer2 = Low_Power_Idle(no_person_timeout_minutes=20)
    recent_motion_time = now - timedelta(minutes=5)  # 5 phút trước có người
    
    test_data_with_person = [
        {'device_id': 'motion_sensor_livingroom', 'motion_detected': True, 'timestamp': recent_motion_time},
        {'device_id': 'smart_plug_tv', 'power': 8.2, 'onOff': True, 'timestamp': now - timedelta(minutes=45)},
        {'device_id': 'smart_plug_tv', 'power': 8.1, 'onOff': True, 'timestamp': now},
    ]
    
    result2 = optimizer2.process_and_recommend(test_data_with_person)
    print(f"   Trạng thái có người: {'CÓ' if result2['person_status']['is_person_present'] else 'KHÔNG'}")
    print(f"   Phút từ lần cuối có motion: {result2['person_status']['minutes_since_last_motion']} phút")
    print(f"   Số khuyến nghị: {len(result2['recommendations'])}")
    
    print("\nMODULE HOẠT ĐỘNG ĐÚNG!")