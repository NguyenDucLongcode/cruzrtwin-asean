# robot/robot_api.py
"""
T-14: Cruz Robot Interface API
REST API để điều khiển robot Cruz
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uvicorn
import time
import random

from robot_simulator import get_robot

# ==================== PYDANTIC MODELS ====================

class NavigationCommand(BaseModel):
    """Lệnh di chuyển"""
    target_zone: str
    x: Optional[float] = None
    y: Optional[float] = None

class AlertCommand(BaseModel):
    """Lệnh hiển thị cảnh báo"""
    message: str
    severity: str  # info, warning, critical
    duration: int = 10
    instruction: Optional[str] = None  # ← Thêm hướng dẫn chi tiết

class VoiceCommand(BaseModel):
    """Lệnh phát giọng nói"""
    text: str
    language: str = "vi-VN"

class DeviceControlCommand(BaseModel):
    """Lệnh điều khiển thiết bị"""
    device_id: str
    action: str  # on, off, toggle

# ==================== FASTAPI APP ====================

app = FastAPI(
    title="Cruz Robot Interface API",
    description="API for controlling Cruz robot in CruzrTwin ASEAN project",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get robot instance
robot = get_robot()

# ==================== HELPER FUNCTIONS ====================

def get_zone_coordinates(zone: str) -> tuple:
    """Lấy tọa độ cho từng khu vực"""
    zones = {
        "living_room": (2.5, 3.0),
        "kitchen": (4.0, 1.5),
        "bedroom": (-1.0, 2.0),
        "bathroom": (-2.0, -1.0),
        "hallway": (0.0, 0.5),
        "home_base": (0.0, 0.0)
    }
    return zones.get(zone, (0, 0))

def get_severity_icon(severity: str) -> str:
    """Lấy icon cho từng mức độ"""
    icons = {
        "info": "ℹ️",
        "warning": "⚠️",
        "critical": "🚨",
        "high": "🔴",
        "none": "✅"
    }
    return icons.get(severity, "🔔")

# ==================== ENDPOINTS ====================

@app.get("/")
def root():
    return {
        "service": "Cruz Robot Interface API",
        "version": "1.0.0",
        "status": "running",
        "robot_type": "Simulator (Mock)",
        "endpoints": [
            "/",
            "/health",
            "/api/robot/status",
            "/api/robot/navigate",
            "/api/robot/alert",
            "/api/robot/speak",
            "/api/robot/device",
            "/api/robot/history",
            "/api/robot/return",
            "/api/robot/instruction"
        ]
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "robot-api",
        "robot_available": True,
        "is_simulator": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/robot/status")
def get_robot_status():
    """Lấy trạng thái hiện tại của robot"""
    return robot.get_status()

@app.post("/api/robot/navigate")
def navigate(command: NavigationCommand):
    """
    Điều khiển robot di chuyển đến khu vực chỉ định
    """
    try:
        # Nếu không có tọa độ, lấy mặc định
        if command.x is None or command.y is None:
            x, y = get_zone_coordinates(command.target_zone)
            command.x, command.y = x, y
        
        result = robot.navigate_to(command.target_zone, command.x, command.y)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/robot/alert")
def show_alert(command: AlertCommand):
    """
    Hiển thị cảnh báo trên màn hình robot
    Có thể kèm hướng dẫn chi tiết (instruction)
    """
    try:
        icon = get_severity_icon(command.severity)
        
        # Gộp instruction vào message nếu có
        if command.instruction:
            full_message = f"{icon} {command.message}\n📋 Hướng dẫn: {command.instruction}"
        else:
            full_message = f"{icon} {command.message}"
        
        # Thêm mức độ cảnh báo
        severity_text = {
            "critical": "⚠️ NGUY HIỂM ⚠️",
            "high": "🔴 CẢNH BÁO",
            "warning": "🟡 CHÚ Ý",
            "info": "🔵 THÔNG BÁO"
        }.get(command.severity, "")
        
        if severity_text:
            full_message = f"{severity_text}\n{full_message}"
        
        result = robot.show_alert(full_message, command.severity, command.duration)
        
        # Nếu là cảnh báo critical, tự động phát giọng nói
        if command.severity == "critical" and command.instruction:
            # Phát giọng nói hướng dẫn
            speak_text = f"Cảnh báo. {command.message}. {command.instruction}"
            robot.speak(speak_text, "vi-VN")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/robot/speak")
def speak(command: VoiceCommand):
    """
    Phát giọng nói qua robot
    """
    try:
        result = robot.speak(command.text, command.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/robot/device")
def control_device(command: DeviceControlCommand):
    """
    Điều khiển thiết bị Matter thông qua robot
    """
    try:
        result = robot.control_device(command.device_id, command.action)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/robot/history")
def get_history():
    """Lấy lịch sử hoạt động của robot"""
    return {
        "navigations": robot.get_navigation_history(),
        "alerts": robot.alert_history[-10:],
        "speeches": robot.speech_history[-10:]
    }

@app.post("/api/robot/return")
def return_to_base():
    """Robot quay về vị trí sạc"""
    try:
        result = robot.return_to_base()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/robot/instruction")
def execute_instruction(instruction: dict):
    """
    Thực thi một hướng dẫn cụ thể
    """
    try:
        action = instruction.get("action")
        target = instruction.get("target", "")
        
        if action == "navigate":
            result = robot.navigate_to(target)
        elif action == "alert":
            result = robot.show_alert(
                instruction.get("message", ""),
                instruction.get("severity", "info"),
                instruction.get("duration", 10)
            )
        elif action == "speak":
            result = robot.speak(instruction.get("text", ""))
        else:
            result = {"success": False, "message": f"Unknown action: {action}"}
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RUN SERVER ====================
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Cruz Robot Interface API Starting...")
    print("   REST API: http://localhost:8001")
    print("   Swagger UI: http://localhost:8001/docs")
    print("   Robot Type: Simulator (Mock)")
    print("=" * 60)
    
    uvicorn.run("robot_api:app", host="0.0.0.0", port=8001, reload=True)