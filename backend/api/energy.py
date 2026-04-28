# backend/api/energy.py
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime
import requests
import httpx
import logging

from services.energy_service import get_energy_stats, get_energy_analysis, execute_energy_commands

router = APIRouter(prefix="/api/energy", tags=["Energy"])
logger = logging.getLogger(__name__)

class ExecuteCommandsRequest(BaseModel):
    dry_run: bool = True
    commands: Optional[List[Dict[str, Any]]] = None

# Lưu trạng thái idle của từng thiết bị (tạm thời)
_idle_tracker = {}

# ==================== ENERGY ENDPOINTS ====================

@router.get("/stats")
def get_energy_stats_endpoint():
    """Lấy thống kê năng lượng"""
    return get_energy_stats().model_dump()


@router.get("/analysis")
def get_energy_analysis_endpoint():
    """Lấy phân tích năng lượng chi tiết (AI + recommendation + command)."""
    return get_energy_analysis()


@router.post("/execute")
def execute_energy_commands_endpoint(request: ExecuteCommandsRequest):
    """Thực thi FIWARE commands (mặc định lấy command từ /api/energy/analysis)."""
    return execute_energy_commands(commands=request.commands, dry_run=request.dry_run)


# Webhook từ FIWARE khi smart plug có power < 10W
@router.post("/check_idle")
async def check_idle(request: Request):
    """
    Webhook từ FIWARE khi smart plug có power < 10W
    """
    payload = await request.json()
    notifications = payload.get("data", [])

    logger.info("[ENERGY] check_idle received payload with %s notification(s)", len(notifications))
    print(f"[ENERGY] check_idle received payload with {len(notifications)} notification(s)", flush=True)
    
   # Xử lý từng notification (có thể có nhiều thiết bị cùng lúc)
    for notification in notifications:
        device_id = notification.get('id') # Lấy ID thiết bị từ notification
        power = notification.get('power', {}).get('value') # Lấy giá trị power từ notification
        timestamp_str = notification.get('TimeInstant', {}).get('value') # Lấy timestamp từ notification
        
        # Nếu thiếu thông tin thiết bị hoặc công suất, bỏ qua notification này
        if not device_id or power is None:
            logger.warning("[ENERGY] Skipping notification without device_id/power: %s", notification)
            continue
        
        # Chuyển timestamp sang datetime object
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        # Kiểm tra thiết bị này đã idle bao lâu
        if device_id not in _idle_tracker:
            _idle_tracker[device_id] = {
                'idle_start': timestamp,
                'first_power': power
            }
            logger.info("[ENERGY] %s bắt đầu idle at %sW", device_id, power)
            print(f"[ENERGY] {device_id} bắt đầu idle at {power}W", flush=True)
            continue  # ← SỬA: dùng continue thay vì return
        
        # Tính thời gian idle
        idle_start = _idle_tracker[device_id]['idle_start']
        idle_duration = (timestamp - idle_start).total_seconds() / 60
        
        if idle_duration >= 30:  # Đã idle 30 phút
            logger.info("⚡ [ENERGY] %s idle %.0f phút -> TẮT!", device_id, idle_duration)
            print(f"⚡ [ENERGY] {device_id} idle {idle_duration:.0f} phút → TẮT!", flush=True)
            
            # Gửi lệnh tắt smart plug
            await turn_off_device(device_id)
            
            # Xóa khỏi tracker
            del _idle_tracker[device_id]
        else:
            logger.info("[ENERGY] %s idle %.0f/%s phút", device_id, idle_duration, 30)
            print(f"[ENERGY] {device_id} idle {idle_duration:.0f}/{30} phút", flush=True)
    
    return {"status": "ok"}


async def turn_off_device(device_id: str):
    """Gửi lệnh tắt smart plug qua FIWARE"""
    # 1. Cập nhật trạng thái onOff trong FIWARE
    url = f"http://localhost:1026/v2/entities/{device_id}/attrs"
    payload = {"onOff": {"type": "Boolean", "value": False}}
    
    try:
        response = requests.patch(url, json=payload)
        if response.status_code == 204:
            logger.info("   Đã tắt %s trên FIWARE", device_id)
            print(f"   Đã tắt {device_id} trên FIWARE", flush=True)
        else:
            logger.error("   Lỗi khi tắt %s: %s", device_id, response.status_code)
            print(f"   Lỗi khi tắt {device_id}: {response.status_code}", flush=True)
    except Exception as e:
        logger.exception("   Không thể kết nối FIWARE")
        print(f"   Không thể kết nối FIWARE: {e}", flush=True)
        return
    
    # 2. Gọi robot thông báo
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://localhost:8001/api/robot/alert",
                json={
                    "message": f"Đã tự động tắt {device_id} (idle 30 phút)",
                    "severity": "info",
                    "duration": 5
                },
                timeout=2.0
            )
            logger.info("   Đã thông báo robot")
            print(f"   Đã thông báo robot", flush=True)
    except Exception as e:
        logger.exception("   Không thể thông báo robot")
        print(f"   Không thể thông báo robot: {e}", flush=True)