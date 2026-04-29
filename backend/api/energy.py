from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime
import requests
import httpx
import logging
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from services.energy_service import get_energy_stats, get_energy_analysis, execute_energy_commands

# Lấy đường dẫn đến thư mục chứa Low_power_idle.py
repo_root = Path(__file__).resolve().parents[2]
energy_dir = repo_root / "ai-models" / "energy"

# Thêm vào sys.path
if str(energy_dir) not in sys.path:
    sys.path.insert(0, str(energy_dir))

# Import - có thể báo lỗi trong IDE nhưng chạy được
Low_power_idle_module = __import__("Low_power_idle")
Low_Power_Idle = Low_power_idle_module.Low_Power_Idle

# Hoặc dùng importlib
import importlib.util
spec = importlib.util.spec_from_file_location(
    "Low_power_idle", 
    energy_dir / "Low_power_idle.py"
)
low_power = importlib.util.module_from_spec(spec)
spec.loader.exec_module(low_power)
Low_Power_Idle = low_power.Low_Power_Idle


#  ==================== API ROUTER ====================
router = APIRouter(prefix="/api/energy", tags=["Energy"])
logger = logging.getLogger(__name__)

# ================= INIT =================
optimizer = Low_Power_Idle(no_person_timeout_minutes=20)

living_room_devices = {}
_idle_tracker = {}

# ================= REQUEST MODEL =================
class ExecuteCommandsRequest(BaseModel):
    dry_run: bool = True
    commands: Optional[List[Dict[str, Any]]] = None


# ================= BASIC APIs =================

@router.get("/stats")
def get_energy_stats_endpoint():
    return get_energy_stats().model_dump()


@router.get("/analysis")
def get_energy_analysis_endpoint():
    return get_energy_analysis()


@router.post("/execute")
def execute_energy_commands_endpoint(request: ExecuteCommandsRequest):
    return execute_energy_commands(commands=request.commands, dry_run=request.dry_run)


# ============================================================
# CORE: PROCESS LIVING ROOM DATA (FIWARE CALLS THIS)
# ============================================================

from datetime import datetime, timedelta
import numpy as np

async def process_livingroom_data(payload: dict = None):
    """
    Xử lý dữ liệu từ living room webhook - DÙNG DATA GIẢ
    Trả về kết quả GIỐNG HỆT test ở Low_power_idle
    """
    
    print("\n" + "="*60)
    print("🏠 LIVING ROOM PROCESSOR (MOCK DATA)")
    print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)
    
    # ===== TẠO DATA GIẢ Y HỆT TEST =====
    now = datetime.now()
    motion_time = now - timedelta(minutes=25)  # 25 phút trước có người
    
    test_data = [
        # Cảm biến chuyển động (PIR sensor)
        {'device_id': 'motion_sensor_livingroom', 'motion_detected': True, 'timestamp': motion_time},
        {'device_id': 'motion_sensor_livingroom', 'motion_detected': False, 'timestamp': motion_time + timedelta(seconds=5)},
        
        # Cảm biến chuyển động khác trong phòng
        {'device_id': 'pir_sensor_hall', 'motion_detected': False, 'timestamp': now - timedelta(minutes=30)},
        
        # TV: idle 45 phút - DÙNG ĐÚNG ID TRONG DATABASE
        {'device_id': 'matter_SmartPlug_001', 'power': 8.2, 'onOff': True, 'timestamp': now - timedelta(minutes=45)},
        {'device_id': 'matter_SmartPlug_001', 'power': 8.1, 'onOff': True, 'timestamp': now - timedelta(minutes=30)},
        {'device_id': 'matter_SmartPlug_001', 'power': 7.9, 'onOff': True, 'timestamp': now},
        
        # Quạt: đang chạy bình thường (không idle)
        {'device_id': 'smart_plug_fan', 'power': 45.0, 'onOff': True, 'timestamp': now},
        
        # Đèn: đã tắt (không xét)
        {'device_id': 'smart_plug_light', 'power': 0, 'onOff': False, 'timestamp': now},
        
        # Điều hòa: công suất cao (đang dùng)
        {'device_id': 'smart_plug_ac', 'power': 850.0, 'onOff': True, 'timestamp': now},
    ]
    
    # ===== TÁCH MOTION DATA VÀ DEVICE DATA =====
    motion_data = []
    device_data = []
    
    for item in test_data:
        device_id = item.get('device_id')
        
        if 'motion' in device_id or 'pir' in device_id:
            motion_data.append({
                'device_id': device_id,
                'motion_detected': item.get('motion_detected', False),
                'timestamp': item.get('timestamp')
            })
        else:
            device_data.append({
                'device_id': device_id,
                'power': item.get('power', 0),
                'onOff': item.get('onOff', False),
                'timestamp': item.get('timestamp')
            })
    
    # ===== CẬP NHẬT MOTION =====
    if motion_data:
        optimizer.update_motion_sensor(motion_data)
    
    # ===== PHÂN TÍCH IDLE DEVICES =====
    result = optimizer.process_and_recommend(device_data)
    
    # ===== IN KẾT QUẢ GIỐNG HỆT TEST =====
    print("\n📊 KẾT QUẢ PHÂN TÍCH:")
    print(f"   Trạng thái có người: {'CÓ' if result['person_status']['is_person_present'] else 'KHÔNG'}")
    print(f"   Phút từ lần cuối có motion: {result['person_status']['minutes_since_last_motion']} phút")
    print(f"   Ngưỡng không người: {result['person_status']['no_person_timeout_minutes']} phút")
    print(f"   Thiết bị đang bật: {result['total_devices_analyzed']}")
    print(f"   Idle devices: {result['idle_devices_found']}")
    print(f"   Tiết kiệm dự kiến: {result['estimated_daily_savings_kwh']:.2f} kWh/ngày")
    
    print("\n💡 KHUYẾN NGHỊ:")
    for rec in result['recommendations']:
        print(f"   → {rec}")
    
    if not result['recommendations']:
        print("   → Không có khuyến nghị tắt thiết bị (có người trong phòng hoặc thiết bị đang hoạt động)")
    
    print("\n📡 FIWARE COMMANDS (để toggle smart plug):")
    for cmd in result['fiware_commands']:
        print(f"   → {cmd}")
    
    print("\n📊 THỐNG KÊ MOTION SENSOR:")
    stats = optimizer.get_motion_statistics()
    print(f"   Lần cuối phát hiện motion: {stats['last_motion_time']}")
    print(f"   Tổng số sự kiện motion: {stats['total_motion_events']}")
    
    # ===== TỰ ĐỘNG TẮT THIẾT BỊ =====
    if result['fiware_commands']:
        print("\n🔌 TỰ ĐỘNG TẮT THIẾT BỊ:")
        for cmd in result['fiware_commands']:
            device_id = cmd['device_id']
            print(f"   → Đang tắt {device_id}...")
            await turn_off_device(device_id)
    
    return {
        "status": "success",
        "person_present": result['person_status']['is_person_present'],
        "minutes_since_motion": result['person_status']['minutes_since_last_motion'],
        "total_devices_on": result['total_devices_analyzed'],
        "idle_devices_found": result['idle_devices_found'],
        "estimated_savings_kwh": result['estimated_daily_savings_kwh'],
        "recommendations": result['recommendations'],
        "fiware_commands": result['fiware_commands']
    }







# ============================================================
# 🔁 FALLBACK: SIMPLE IDLE TRACK (OPTIONAL)
# ============================================================

@router.post("/check_idle")
async def check_idle(request: Request):
    payload = await request.json()
    notifications = payload.get("data", [])

    for notification in notifications:
        device_id = notification.get('id')
        power = notification.get('power', {}).get('value')

        if not device_id or power is None:
            continue

        timestamp = datetime.now()
        await process_idle_device(device_id, power, timestamp)

    return {"status": "ok"}


async def process_idle_device(device_id: str, power: float, timestamp: datetime):
    if device_id not in _idle_tracker:
        _idle_tracker[device_id] = {'idle_start': timestamp}
        return

    idle_duration = (timestamp - _idle_tracker[device_id]['idle_start']).total_seconds() / 60

    if idle_duration >= 30:
        print(f"⚡ {device_id} idle {idle_duration:.0f} phút → TẮT")
        await turn_off_device(device_id)
        del _idle_tracker[device_id]


# ============================================================
# 🔌 TURN OFF DEVICE (FIWARE)
# ============================================================

async def turn_off_device(device_id: str ):
    url = f"http://localhost:1026/v2/entities/{device_id}/attrs"
    payload = {"onOff": {"type": "Boolean", "value": False}}

    try:
        response = requests.patch(url, json=payload)
        if response.status_code == 204:
            print(f"   OFF {device_id}")
        else:
            print(f"   ERROR {device_id}")
    except Exception as e:
        print(f"   FIWARE ERROR: {e}")
        return

    # robot alert
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://localhost:8001/api/robot/alert",
                json={
                    "message": f"Đã tắt {device_id}",
                    "severity": "info",
                },
                timeout=2.0
            )
    except:
        pass



# ============================================================
# 📊 STATUS API
# ============================================================

@router.get("/livingroom/status")
async def livingroom_status():
    is_present, minutes_since = optimizer.is_person_present()

    return {
        "person": is_present,
        "minutes_since_motion": round(minutes_since, 1),
        "devices": living_room_devices
    }


@router.get("/livingroom/devices")
async def get_livingroom_devices():
    return {
        "devices": living_room_devices,
        "count": len(living_room_devices)
    }