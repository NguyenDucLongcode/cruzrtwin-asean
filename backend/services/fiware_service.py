import requests
from typing import List, Dict, Optional
from config import FIWARE_ORION_URL


def _extract_onoff_payload(command: Dict) -> Optional[Dict]:
    payload = command.get("payload")
    if not isinstance(payload, dict):
        return None
    on_off = payload.get("onOff")
    if not isinstance(on_off, dict) or "value" not in on_off:
        return None
    return {
        "onOff": {
            "type": "Boolean",
            "value": bool(on_off.get("value")),
        }
    }

def get_entities(entity_type: str = None) -> List[Dict]:
    """Lấy entities từ FIWARE Orion"""
    try:
        url = f"{FIWARE_ORION_URL}/entities"
        params = {}
        if entity_type:
            params['type'] = entity_type
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error connecting to Orion: {e}")
        return []

def get_entity_by_id(entity_id: str) -> Optional[Dict]:
    """Lấy entity theo ID"""
    try:
        url = f"{FIWARE_ORION_URL}/entities/{entity_id}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def parse_entity_to_sensor(entity: Dict):
    """Chuyển entity từ Orion sang SensorData object"""
    from models import SensorData
    from datetime import datetime
    
    return SensorData(
        device_id=entity.get('id', 'unknown'),
        device_type=entity.get('type', 'unknown'),
        temperature=entity.get('temperature', {}).get('value'),
        humidity=entity.get('humidity', {}).get('value'),
        smokeLevel=entity.get('smokeLevel', {}).get('value'),
        pm25=entity.get('pm25', {}).get('value'),
        pm10=entity.get('pm10', {}).get('value'),
        co2=entity.get('co2', {}).get('value'),
        tvoc=entity.get('tvoc', {}).get('value'),
        aqi=entity.get('aqi', {}).get('value'),
        power=entity.get('power', {}).get('value'),
        voltage=entity.get('voltage', {}).get('value'),
        current=entity.get('current', {}).get('value'),
        energyToday=entity.get('energyToday', {}).get('value'),
        onOff=entity.get('onOff', {}).get('value'),
        battery=entity.get('battery', {}).get('value'),
        status=entity.get('status', {}).get('value'),
        alarm=entity.get('alarm', {}).get('value'),
        timestamp=entity.get('TimeInstant', {}).get('value', datetime.now().isoformat())
    )


def execute_fiware_command(command: Dict, dry_run: bool = True) -> Dict:
    """Thực thi FIWARE command cho SmartPlug (hiện hỗ trợ toggle onOff)."""
    command_name = command.get("command")
    device_id = command.get("device_id")

    if command_name != "toggle_smart_plug":
        return {
            "success": False,
            "device_id": device_id,
            "command": command_name,
            "status_code": None,
            "message": "Unsupported command",
            "dry_run": dry_run,
        }

    attrs_payload = _extract_onoff_payload(command)
    if not device_id or attrs_payload is None:
        return {
            "success": False,
            "device_id": device_id,
            "command": command_name,
            "status_code": None,
            "message": "Invalid command payload",
            "dry_run": dry_run,
        }

    if dry_run:
        return {
            "success": True,
            "device_id": device_id,
            "command": command_name,
            "status_code": None,
            "message": "Dry-run: command validated",
            "dry_run": True,
            "request": {
                "url": f"{FIWARE_ORION_URL}/entities/{device_id}/attrs",
                "payload": attrs_payload,
            },
        }

    try:
        response = requests.patch(
            f"{FIWARE_ORION_URL}/entities/{device_id}/attrs",
            json=attrs_payload,
            timeout=5,
        )
        success = response.status_code == 204
        return {
            "success": success,
            "device_id": device_id,
            "command": command_name,
            "status_code": response.status_code,
            "message": "Executed" if success else response.text,
            "dry_run": False,
        }
    except Exception as exc:
        return {
            "success": False,
            "device_id": device_id,
            "command": command_name,
            "status_code": None,
            "message": f"Execution error: {exc}",
            "dry_run": False,
        }