from typing import Optional, List, Dict, Any

from fastapi import APIRouter
from pydantic import BaseModel

from services.energy_service import get_energy_stats, get_energy_analysis, execute_energy_commands

router = APIRouter(prefix="/api/energy", tags=["Energy"])


class ExecuteCommandsRequest(BaseModel):
    dry_run: bool = True
    commands: Optional[List[Dict[str, Any]]] = None

# ==================== ENERGY ENDPOINTS ====================

# Endpoint để lấy thống kê năng lượng
@router.get("/stats")
def get_energy_stats_endpoint():
    """Lấy thống kê năng lượng"""
    return get_energy_stats().model_dump()


# Endpoint để lấy phân tích năng lượng chi tiết (AI + recommendation + command)
@router.get("/analysis")
def get_energy_analysis_endpoint():
    """Lấy phân tích năng lượng chi tiết (AI + recommendation + command)."""
    return get_energy_analysis()


# Endpoint để thực thi các lệnh điều khiển năng lượng (từ recommendation hoặc tùy chọn)
@router.post("/execute")
def execute_energy_commands_endpoint(request: ExecuteCommandsRequest):
    """Thực thi FIWARE commands (mặc định lấy command từ /api/energy/analysis)."""
    return execute_energy_commands(commands=request.commands, dry_run=request.dry_run)