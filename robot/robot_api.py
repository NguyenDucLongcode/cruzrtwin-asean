from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uvicorn

from robot_simulator import get_robot

# ==================== PYDANTIC MODELS ====================

class NavigationCommand(BaseModel):
    """Lệnh di chuyển"""
    target_zone: str  # living_room, kitchen, bedroom, bathroom, hallway
    x: Optional[float] = None
    y: Optional[float] = None

class AlertCommand(BaseModel):
    """Lệnh hiển thị cảnh báo"""
    message: str
    severity: str  # info, warning, critical
    duration: int = 10

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
            "/api/robot/return"
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
    
    - **target_zone**: living_room, kitchen, bedroom, bathroom, hallway
    - **x, y**: tọa độ cụ thể (optional)
    """
    try:
        result = robot.navigate_to(command.target_zone, command.x, command.y)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/robot/alert")
def show_alert(command: AlertCommand):
    """
    Hiển thị cảnh báo trên màn hình robot
    
    - **message**: Nội dung cảnh báo
    - **severity**: info, warning, critical
    - **duration**: Thời gian hiển thị (giây)
    """
    try:
        result = robot.show_alert(command.message, command.severity, command.duration)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/robot/speak")
def speak(command: VoiceCommand):
    """
    Phát giọng nói qua robot
    
    - **text**: Nội dung cần nói
    - **language**: vi-VN hoặc en-US
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
    
    - **device_id**: ID của thiết bị (smart plug)
    - **action**: on, off, toggle
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
        "alerts": robot.alert_history[-10:],  # 10 gần nhất
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


# ==================== RUN SERVER ====================
if __name__ == "__main__":
    print("=" * 60)
    print(" Cruz Robot Interface API Starting...")
    print("   REST API: http://localhost:8001")
    print("   Swagger UI: http://localhost:8001/docs")
    print("   Robot Type: Simulator (Mock)")
    print("=" * 60)
    
    uvicorn.run("robot_api:app", host="0.0.0.0", port=8001, reload=True)