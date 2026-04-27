from models import EnergyStats
from services.fiware_service import get_entities, parse_entity_to_sensor
from services.fiware_service import execute_fiware_command
from services.fiware_service import get_attr_history_quantumleap
from config import IDLE_POWER_THRESHOLD, ENERGY_HISTORY_LAST_N
from datetime import datetime
from pathlib import Path
import importlib.util
import io
from contextlib import redirect_stdout

_ENERGY_OPTIMIZER = None
_ENERGY_OPTIMIZER_LOAD_ERROR = None



# Helper function để lấy root của project, dùng để tìm file AI model/optimizer
def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


# Helper function để load AI energy optimizer class từ file, nếu có
def _load_energy_optimizer_class():
    root = _project_root()
    optimizer_path = root / "ai-models" / "energy" / "energy_optimizer.py"
    if not optimizer_path.exists():
        raise FileNotFoundError(f"Energy optimizer not found: {optimizer_path}")

    spec = importlib.util.spec_from_file_location("energy_optimizer_module", optimizer_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.EnergyOptimizer


# Singleton pattern để load AI energy optimizer (nếu có), tránh load nhiều lần trong cùng một phiên chạy
def _get_energy_optimizer():
    global _ENERGY_OPTIMIZER, _ENERGY_OPTIMIZER_LOAD_ERROR
    if _ENERGY_OPTIMIZER is not None:
        return _ENERGY_OPTIMIZER
    if _ENERGY_OPTIMIZER_LOAD_ERROR is not None:
        return None

    try:
        EnergyOptimizer = _load_energy_optimizer_class()
        with redirect_stdout(io.StringIO()):
            _ENERGY_OPTIMIZER = EnergyOptimizer()
        return _ENERGY_OPTIMIZER
    except Exception as exc:
        _ENERGY_OPTIMIZER_LOAD_ERROR = str(exc)
        return None


# Helper function để build dữ liệu thiết bị từ entities FIWARE, chuẩn bị cho AI optimizer
def _build_plug_device_data(smart_plugs):
    device_data = []
    for plug in smart_plugs:
        sensor = parse_entity_to_sensor(plug)
        history = get_attr_history_quantumleap(
            entity_id=sensor.device_id,
            attr_name="power",
            last_n=ENERGY_HISTORY_LAST_N,
        )

        if history:
            for item in history:
                device_data.append({
                    "device_id": sensor.device_id,
                    "power": item.get("value"),
                    "onOff": sensor.onOff,
                    "timestamp": item.get("timestamp"),
                })
            continue

        # Fallback: nếu chưa có time-series thì vẫn dùng snapshot hiện tại từ Orion.
        device_data.append({
            "device_id": sensor.device_id,
            "power": sensor.power,
            "onOff": sensor.onOff,
            "timestamp": sensor.timestamp,
        })
    return device_data

# Phân tích năng lượng đầy đủ, ưu tiên dùng AI optimizer.
#  Nếu AI optimizer không load được, fallback về rule-based analysis đơn giản.
def get_energy_analysis() -> dict:
    """Phân tích năng lượng đầy đủ, ưu tiên dùng AI optimizer."""
    entities = get_entities()
    smart_plugs = [e for e in entities if e.get('type') == 'SmartPlug']
    analyzed_at = datetime.now().isoformat()

    optimizer = _get_energy_optimizer()
    if optimizer is not None:
        device_data = _build_plug_device_data(smart_plugs)
        ai_result = optimizer.process_and_recommend(device_data)

        current_device_states = []
        for plug in smart_plugs:
            sensor = parse_entity_to_sensor(plug)
            current_device_states.append({
                "device_id": sensor.device_id,
                "power": sensor.power or 0.0,
                "onOff": bool(sensor.onOff),
            })

        total_power = 0.0
        idle_devices = []
        for item in current_device_states:
            power = item.get("power") or 0.0
            is_on = bool(item.get("onOff"))
            if is_on:
                total_power += power
            if is_on and power < IDLE_POWER_THRESHOLD:
                idle_devices.append(item.get("device_id"))

        return {
            "mode": "ai",
            "stats": {
                "total_power": round(total_power, 1),
                "idle_devices": idle_devices,
                "estimated_savings": round(ai_result.get("estimated_daily_savings_kwh", 0.0), 2),
                "timestamp": analyzed_at,
            },
            "recommendations": ai_result.get("recommendations", []),
            "fiware_commands": ai_result.get("fiware_commands", []),
            "meta": {
                "total_devices_analyzed": ai_result.get("total_devices_analyzed", 0),
                "idle_devices_found": ai_result.get("idle_devices_found", 0),
                "history_points_used": len(device_data),
            },
        }

    # Fallback nếu chưa load được AI model/optimizer
    total_power = 0.0
    idle_devices = []
    for plug in smart_plugs:
        sensor = parse_entity_to_sensor(plug)
        if sensor.onOff:
            total_power += sensor.power or 0.0
            if (sensor.power or 0.0) < IDLE_POWER_THRESHOLD:
                idle_devices.append(sensor.device_id)

    return {
        "mode": "rule-based",
        "stats": {
            "total_power": round(total_power, 1),
            "idle_devices": idle_devices,
            "estimated_savings": round(len(idle_devices) * 0.05, 2),
            "timestamp": analyzed_at,
        },
        "recommendations": [
            f"Xem xét tắt thiết bị idle: {device_id}" for device_id in idle_devices
        ],
        "fiware_commands": [],
        "meta": {
            "total_devices_analyzed": len(smart_plugs),
            "idle_devices_found": len(idle_devices),
            "load_error": _ENERGY_OPTIMIZER_LOAD_ERROR,
        },
    }

# API để dashboard gọi lấy thống kê năng lượng
def get_energy_stats() -> EnergyStats:
    """Lấy thống kê năng lượng từ smart plugs"""
    analysis = get_energy_analysis()
    stats = analysis["stats"]

    return EnergyStats(
        total_power=stats["total_power"],
        idle_devices=stats["idle_devices"],
        estimated_savings=stats["estimated_savings"],
        timestamp=stats["timestamp"]
    )

# AI → generate command → gửi xuống FIWARE
def execute_energy_commands(commands=None, dry_run: bool = True) -> dict:
    """Thực thi các FIWARE command (mặc định lấy từ kết quả AI energy analysis)."""
    command_list = commands
    source = "request"

    if command_list is None:
        analysis = get_energy_analysis()
        command_list = analysis.get("fiware_commands", [])
        source = "ai-analysis"

    if not isinstance(command_list, list):
        return {
            "success": False,
            "source": source,
            "dry_run": dry_run,
            "total_commands": 0,
            "executed": 0,
            "failed": 1,
            "results": [
                {
                    "success": False,
                    "message": "commands must be a list",
                }
            ],
        }

    results = [execute_fiware_command(cmd, dry_run=dry_run) for cmd in command_list]
    executed = sum(1 for item in results if item.get("success"))
    failed = len(results) - executed

    return {
        "success": failed == 0,
        "source": source,
        "dry_run": dry_run,
        "total_commands": len(command_list),
        "executed": executed,
        "failed": failed,
        "results": results,
    }