import time
import random
from datetime import datetime
from typing import Dict, Any

class CruzRobotSimulator:
    """Mô phỏng robot Cruz (dùng khi không có robot thật)"""
    
    def __init__(self):
        self.current_position = {"zone": "home_base", "x": 0, "y": 0}
        self.status = "idle"
        self.battery = 100
        self.alert_history = []
        self.speech_history = []
        self.navigation_history = []
        
    def navigate_to(self, target_zone: str, x: float = None, y: float = None) -> Dict:
        """
        Di chuyển robot đến khu vực chỉ định
        
        Args:
            target_zone: "living_room", "kitchen", "bedroom", "bathroom", "hallway"
            x, y: tọa độ cụ thể (optional)
        
        Returns:
            Kết quả di chuyển
        """
        print(f"\n🤖 [ROBOT] Navigating to: {target_zone}")
        print(f"   From: {self.current_position['zone']}")
        
        # Mô phỏng thời gian di chuyển
        travel_time = random.uniform(2, 5)
        time.sleep(travel_time)
        
        # Cập nhật vị trí
        self.current_position = {
            "zone": target_zone,
            "x": x if x else random.uniform(-5, 5),
            "y": y if y else random.uniform(-5, 5)
        }
        self.battery -= travel_time * 2  # Giảm pin
        
        # Lưu lịch sử
        self.navigation_history.append({
            "timestamp": datetime.now().isoformat(),
            "from_zone": self.current_position['zone'] if len(self.navigation_history) > 0 else "home_base",
            "to_zone": target_zone,
            "travel_time": round(travel_time, 1)
        })
        
        print(f"   ✅ Arrived at: {target_zone} (took {travel_time:.1f}s)")
        print(f"   🔋 Battery: {self.battery:.0f}%")
        
        return {
            "success": True,
            "message": f"Robot arrived at {target_zone}",
            "position": self.current_position,
            "travel_time": round(travel_time, 1),
            "battery": round(self.battery, 1)
        }
    
    def show_alert(self, message: str, severity: str, duration: int = 10) -> Dict:
        """
        Hiển thị cảnh báo trên màn hình robot
        
        Args:
            message: Nội dung cảnh báo
            severity: "info", "warning", "critical"
            duration: Thời gian hiển thị (giây)
        """
        severity_icon = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🚨"
        }.get(severity, "🔔")
        
        print(f"\n{severity_icon} [ROBOT ALERT] ({severity.upper()}): {message}")
        print(f"   📱 Displaying on robot screen for {duration}s")
        
        # Mô phỏng hiển thị
        time.sleep(0.5)
        
        # Lưu lịch sử
        self.alert_history.append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "severity": severity,
            "duration": duration
        })
        
        return {
            "success": True,
            "message": f"Alert displayed: {message}",
            "severity": severity
        }
    
    def speak(self, text: str, language: str = "vi-VN") -> Dict:
        """
        Phát giọng nói qua robot
        
        Args:
            text: Nội dung cần nói
            language: Ngôn ngữ (vi-VN, en-US)
        """
        print(f"\n🗣️ [ROBOT SPEECH] ({language}): {text}")
        
        # Mô phỏng thời gian nói
        speech_time = len(text) / 15  # ~15 ký tự/giây
        time.sleep(min(speech_time, 3))
        
        # Lưu lịch sử
        self.speech_history.append({
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "language": language
        })
        
        return {
            "success": True,
            "message": f"Speech played: {text[:50]}...",
            "duration": round(speech_time, 1)
        }
    
    def control_device(self, device_id: str, action: str) -> Dict:
        """
        Điều khiển thiết bị Matter thông qua robot
        
        Args:
            device_id: ID của smart plug/thiết bị
            action: "on", "off", "toggle"
        """
        print(f"\n🔌 [ROBOT DEVICE] {action.upper()} {device_id}")
        
        # Mô phỏng gửi lệnh Matter
        time.sleep(0.3)
        
        return {
            "success": True,
            "device_id": device_id,
            "action": action,
            "status": "executed",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        """Lấy trạng thái robot"""
        return {
            "status": self.status,
            "position": self.current_position,
            "battery": round(self.battery, 1),
            "alerts_count": len(self.alert_history),
            "speech_count": len(self.speech_history),
            "navigation_count": len(self.navigation_history),
            "is_simulator": True
        }
    
    def get_navigation_history(self) -> list:
        """Lấy lịch sử di chuyển"""
        return self.navigation_history
    
    def return_to_base(self) -> Dict:
        """Quay về vị trí sạc"""
        return self.navigate_to("home_base", 0, 0)


# Singleton instance
_robot_instance = None

def get_robot():
    global _robot_instance
    if _robot_instance is None:
        _robot_instance = CruzRobotSimulator()
    return _robot_instance