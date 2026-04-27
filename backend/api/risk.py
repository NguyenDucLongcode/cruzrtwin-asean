from fastapi import APIRouter, HTTPException
from services.fiware_service import get_entities, get_entity_by_id, parse_entity_to_sensor
from services.risk_service import calculate_risk_score
from datetime import datetime

router = APIRouter(prefix="/api/risk", tags=["Risk"])

@router.get("/summary")
def get_risk_summary():
    """Lấy tổng quan risk score"""
    entities = get_entities()
    
    summary = []
    high_risk_count = 0
    
    for entity in entities:
        sensor_data = parse_entity_to_sensor(entity)
        risk = calculate_risk_score(sensor_data)
        summary.append({
            "device_id": sensor_data.device_id,
            "device_type": sensor_data.device_type,
            "risk_score": risk.score,
            "risk_level": risk.level
        })
        if risk.level == "critical":
            high_risk_count += 1
    
    return {
        "devices": summary,
        "summary": {
            "total_devices": len(summary),
            "high_risk_count": high_risk_count,
            "overall_level": "critical" if high_risk_count > 0 else "good"
        },
        "timestamp": datetime.now().isoformat()
    }

@router.get("/{device_id}")
def get_device_risk(device_id: str):
    """Lấy risk score cho 1 thiết bị"""
    entity = get_entity_by_id(device_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    
    sensor_data = parse_entity_to_sensor(entity)
    risk = calculate_risk_score(sensor_data)
    
    return {
        "device_id": device_id,
        "risk": risk.model_dump(),
        "timestamp": datetime.now().isoformat()
    }