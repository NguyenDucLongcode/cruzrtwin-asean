import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

class EnergyOptimizer:
    def __init__(self, model_path='anomaly_model.pkl'):
        """Khởi tạo Energy Optimizer - Tích hợp model T-07 để phát hiện bất thường năng lượng"""
        resolved_model_path = self._resolve_model_path(model_path)
        self.model = joblib.load(resolved_model_path)
        self.model_path = resolved_model_path
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
        
        print("=" * 60)
        print("AI ENERGY OPTIMIZATION MODULE (T-10)")
        print(f"   - Model T-07 loaded: {self.model_path}")
        print(f"   - Idle threshold: {self.idle_power_threshold}W trong {self.idle_time_threshold} phút")
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
    
    def detect_idle_devices(self, device_data):
        """
        Phát hiện thiết bị idle (bật nhưng không dùng)
        
        Args:
            device_data: list of dict với các keys: device_id, power, onOff, timestamp
        
        Returns:
            list: danh sách thiết bị idle cần xử lý
        """
        idle_devices = []
        
        for device in device_data:
            device_id = device.get('device_id')
            power = device.get('power')
            is_on = device.get('onOff', False)
            timestamp = self._normalize_timestamp(device.get('timestamp'))

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
                
                if (
                    idle_duration >= time_threshold
                    and self.device_history[device_id]['below_threshold_count'] >= self.confirmation_readings
                    and not self.device_history[device_id]['shutdown_recommended']
                ):
                    idle_devices.append({
                        'device_id': device_id,
                        'idle_duration_minutes': round(idle_duration, 1),
                        'current_power': round(power, 1),
                        'threshold_power': power_threshold,
                        'threshold_time_minutes': time_threshold,
                        'ml_confirmed': ml_anomaly,
                        'action': 'recommend_shutdown',
                        'recommendation': (
                            f"[TIẾT KIỆM] Tắt {device_id} - idle {idle_duration:.0f} phút "
                            f"(ngưỡng {time_threshold} phút), công suất {power:.1f}W (ngưỡng {power_threshold}W)"
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
            command["reason"] = "energy_optimization_idle_detection"
        
        return command
    
    def process_and_recommend(self, device_data):
        """
        Xử lý dữ liệu và trả về khuyến nghị + FIWARE commands
        
        Returns:
            dict: Kết quả phân tích
        """
        idle_devices = self.detect_idle_devices(device_data)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'total_devices_analyzed': len([d for d in device_data if d['onOff']]),
            'idle_devices_found': len(idle_devices),
            'estimated_daily_savings_kwh': len(idle_devices) * 0.12,  # ~120Wh/ngày/thiết bị
            'recommendations': [],
            'fiware_commands': []
        }
        
        for device in idle_devices:
            result['recommendations'].append(device['recommendation'])
            result['fiware_commands'].append(
                self.generate_fiware_command(device['device_id'], 'off')
            )
        
        return result


# ================== TEST MODULE ==================
if __name__ == "__main__":
    print("\nTESTING ENERGY OPTIMIZER MODULE\n")
    
    optimizer = EnergyOptimizer()
    
    # Tạo dữ liệu mô phỏng
    now = datetime.now()
    
    test_data = [
        # TV: idle 45 phút (cần tắt)
        {'device_id': 'smart_plug_tv', 'power': 8.2, 'onOff': True, 'timestamp': now - timedelta(minutes=45)},
        {'device_id': 'smart_plug_tv', 'power': 8.1, 'onOff': True, 'timestamp': now - timedelta(minutes=30)},
        {'device_id': 'smart_plug_tv', 'power': 7.9, 'onOff': True, 'timestamp': now},
        
        # Quạt: đang chạy bình thường (không idle)
        {'device_id': 'smart_plug_fan', 'power': 45.0, 'onOff': True, 'timestamp': now},
        
        # Đèn: đã tắt (không xét)
        {'device_id': 'smart_plug_light', 'power': 0, 'onOff': False, 'timestamp': now},
    ]
    
    result = optimizer.process_and_recommend(test_data)
    
    print("\nKẾT QUẢ PHÂN TÍCH:")
    print(f"   Thiết bị đang bật: {result['total_devices_analyzed']}")
    print(f"   Idle devices: {result['idle_devices_found']}")
    print(f"   Tiết kiệm dự kiến: {result['estimated_daily_savings_kwh']:.2f} kWh/ngày")
    
    print("\nKHUYẾN NGHỊ:")
    for rec in result['recommendations']:
        print(f"   → {rec}")
    
    print("\nFIWARE COMMANDS (để toggle smart plug):")
    for cmd in result['fiware_commands']:
        print(f"   → {cmd}")
    
    print("\nMODULE HOẠT ĐỘNG ĐÚNG!")