from fastapi import APIRouter, HTTPException,status
from services.fiware_service import get_entities, get_entity_by_id, parse_entity_to_sensor
from models import SensorData
from typing import List

router = APIRouter(prefix="/api/sensors", tags=["Sensors"])

@router.get("/{device_id}", response_model=SensorData)
def get_sensor_by_id(device_id: str):
    """Lấy dữ liệu của 1 cảm biến"""
    entity = get_entity_by_id(device_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    return parse_entity_to_sensor(entity)

@router.get("/", response_model=List[SensorData])
def get_all_sensors():
    """Lấy tất cả dữ liệu cảm biến"""
    try:
        entities = get_entities()
        if not entities:
            # Trả về mảng rỗng thay vì lỗi
            return []
        return [parse_entity_to_sensor(e) for e in entities]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Không thể kết nối đến FIWARE: {str(e)}"
        )