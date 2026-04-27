from datetime import datetime
import httpx
from typing import Dict, Any

# Xử lý alert từ FIWARE webhook, broadcast WebSocket, gửi robot
# Robot API URL (T-14 sẽ chạy ở port 8001)
ROBOT_API_URL = "http://localhost:8001/api/robot/alert"

def generate_alert_message(entity_type: str, data: Dict) -> str:
    """Tạo message từ dữ liệu bất thường"""
    if "temperature" in data:
        return f"⚠️ Nhiệt độ cao! {data['temperature']}°C - Kiểm tra ngay!"
    elif "smokeLevel" in data:
        return f"🚨 CẢNH BÁO CHÁY! Khói: {data['smokeLevel']}ppm - Sơ tán khẩn cấp!"
    elif "co2" in data:
        return f"🌫️ CO2 cao! {data['co2']}ppm - Mở cửa sổ ngay!"
    else:
        return f"⚠️ Phát hiện bất thường tại {entity_type}"

def parse_webhook_payload(payload: Dict) -> list:
    """Parse webhook payload từ FIWARE, trả về list alerts"""
    alerts = []
    
    for notification in payload.get('data', []):
        entity_id = notification.get('id')
        entity_type = notification.get('type')
        
        # Lấy giá trị attribute bất thường
        anomaly_data = {}
        for key, value in notification.items():
            if key not in ['id', 'type', 'TimeInstant']:
                if isinstance(value, dict) and 'value' in value:
                    anomaly_data[key] = value['value']
        
        alert = {
            "type": "anomaly_alert",
            "severity": "critical",
            "device_id": entity_id,
            "device_type": entity_type,
            "data": anomaly_data,
            "message": generate_alert_message(entity_type, anomaly_data),
            "timestamp": datetime.now().isoformat()
        }
        alerts.append(alert)
    
    return alerts

async def broadcast_alert(alert: Dict):
    """Broadcast alert qua WebSocket đến dashboard"""
    from services.websocket_manager import manager
    await manager.broadcast(alert)

async def send_to_robot_queue(alert: Dict):
    """
    Gửi alert đến robot queue (cho T-14)
    Robot sẽ nhận lệnh navigation đến khu vực có vấn đề
    """
    try:
        async with httpx.AsyncClient() as client:
            await client.post(ROBOT_API_URL, json=alert, timeout=2.0)
            print(f"   🤖 Forwarded to robot queue")
            return True
    except:
        print(f"   ⚠️ Robot API not available (T-14 not running yet)")
        return False

async def process_anomaly_alert(payload: Dict) -> list:
    """
    Xử lý anomaly alert từ webhook
    Returns: list of alerts đã xử lý
    """
    alerts = parse_webhook_payload(payload)
    
    for alert in alerts:
        print(f"\n🔔 [ALERT] {alert['timestamp']}")
        print(f"   📢 {alert['message']}")
        
        # Broadcast WebSocket
        await broadcast_alert(alert)
        
        # Gửi robot
        await send_to_robot_queue(alert)
    
    return alerts