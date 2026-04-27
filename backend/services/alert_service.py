from datetime import datetime
import httpx
from typing import Dict, Any
from collections import deque

# Xử lý alert từ FIWARE webhook, broadcast WebSocket, gửi robot
# Robot API URL (T-14 sẽ chạy ở port 8001)
ROBOT_API_URL = "http://127.0.0.1:8001/api/robot/alert"
ALERT_HISTORY_LIMIT = 200
_ALERT_HISTORY = deque(maxlen=ALERT_HISTORY_LIMIT)


def store_alert(alert: Dict[str, Any]):
    """Lưu alert vào bộ nhớ tạm để API có thể truy vấn nhanh."""
    _ALERT_HISTORY.append(dict(alert))


def get_recent_alerts(limit: int = 20) -> list:
    """Lấy danh sách alert gần nhất (oldest -> newest)."""
    safe_limit = max(1, min(limit, ALERT_HISTORY_LIMIT))
    items = list(_ALERT_HISTORY)
    return items[-safe_limit:]


def get_latest_alert() -> Dict[str, Any] | None:
    """Lấy alert mới nhất, trả về None nếu chưa có dữ liệu."""
    if not _ALERT_HISTORY:
        return None
    return dict(_ALERT_HISTORY[-1])

# Helper function để đảm bảo text an toàn cho console (tránh lỗi encoding)
def _safe_console_text(text: str) -> str:
    """Return a console-safe version of text for non-UTF8 terminals."""
    return text.encode("ascii", errors="replace").decode("ascii")

# Tạo message alert dựa trên entity type và dữ liệu bất thường
def generate_alert_message(entity_type: str, data: Dict) -> str:
    """Tạo message từ dữ liệu bất thường"""
    if "temperature" in data:
        return f"Nhiệt độ cao! {data['temperature']}°C - Kiểm tra ngay!"
    elif "smokeLevel" in data:
        return f"CẢNH BÁO CHÁY! Khói: {data['smokeLevel']}ppm - Sơ tán khẩn cấp!"
    elif "co2" in data:
        return f"CO2 cao! {data['co2']}ppm - Mở cửa sổ ngay!"
    else:
        return f"Phát hiện bất thường tại {entity_type}"

# Phân tích payload từ FIWARE webhook, trích xuất thông tin alert
def parse_webhook_payload(payload: Dict) -> list:
    """Parse webhook payload từ FIWARE, trả về list alerts"""
    alerts = []
    
    # FIWARE có thể gửi nhiều notification trong một payload, xử lý từng cái
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

# Gửi alert qua WebSocket đến dashboard
async def broadcast_alert(alert: Dict):
    """Broadcast alert qua WebSocket đến dashboard"""
    from services.websocket_manager import manager
    await manager.broadcast(alert)

# Gửi alert đến robot queue (T-14 sẽ nhận lệnh navigation)
async def send_to_robot_queue(alert: Dict):
    """
    Gửi alert đến robot queue (cho T-14)
    Robot sẽ nhận lệnh navigation đến khu vực có vấn đề
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(ROBOT_API_URL, json=alert, timeout=3.0)
            if 200 <= response.status_code < 300:
                print(f"   [ROBOT] Forwarded to robot queue (status={response.status_code})")
                return True

            print(f"   [WARN] Robot API responded non-2xx (status={response.status_code})")
            return False
    except Exception as exc:
        print(f"   [WARN] Robot API not available: {type(exc).__name__}: {exc}")
        return False
    
# Main function để xử lý anomaly alert từ webhook
async def process_anomaly_alert(payload: Dict) -> list:
    """
    Xử lý anomaly alert từ webhook
    Returns: list of alerts đã xử lý
    """
    alerts = parse_webhook_payload(payload)
    
    for alert in alerts:
        print(f"\n[ALERT] {_safe_console_text(alert['timestamp'])}")
        print(f"   [MSG] {_safe_console_text(alert['message'])}")
        
        # Broadcast WebSocket
        await broadcast_alert(alert)
        
        # Gửi robot
        alert["robot_forwarded"] = await send_to_robot_queue(alert)
        store_alert(alert)
    
    return alerts