from fastapi import APIRouter, HTTPException
from services.fiware_service import get_entities, get_entity_by_id, parse_entity_to_sensor
from services.risk_service import calculate_risk_score
from datetime import datetime

router = APIRouter(prefix="/api/risk", tags=["Risk"])

# ==================== RISK ENDPOINTS ====================

# Endpoint để lấy tổng quan risk score cho tất cả thiết bị
# summary tổng thể và chi tiết theo thiết bị, highlight các thiết bị có risk cao
# Endpoint này sẽ giúp dashboard hiển thị nhanh tình hình rủi ro hiện tại của toàn bộ hệ thống, đồng thời cung cấp thông tin chi tiết cho từng thiết bị để người dùng có thể dễ dàng nhận biết và xử lý các vấn đề tiềm ẩn.
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


# Endpoint để lấy risk score cho 1 thiết bị cụ thể
# Endpoint này sẽ giúp người dùng có thể kiểm tra chi tiết mức độ rủi ro của từng thiết bị,
#  từ đó có thể đưa ra các biện pháp xử lý phù hợp để giảm thiểu rủi ro và đảm bảo an toàn cho hệ thống.
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