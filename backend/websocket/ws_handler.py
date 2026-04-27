from fastapi import WebSocket, WebSocketDisconnect
from services.websocket_manager import manager
from services.fiware_service import get_entities, parse_entity_to_sensor
from config import WEBSOCKET_BROADCAST_INTERVAL, ALERT_THRESHOLD_TEMP, ALERT_THRESHOLD_SMOKE
from datetime import datetime
import asyncio

async def websocket_handler(websocket: WebSocket):
    """Xử lý WebSocket connection"""
    await manager.connect(websocket)
    
    try:
        await websocket.send_json({
            "type": "connection",
            "message": "Connected",
            "timestamp": datetime.now().isoformat()
        })
        
        last_alert_sent = {}
        
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_json({"type": "pong"})
            
            # Check anomalies from FIWARE
            entities = get_entities()
            for entity in entities:
                sensor = parse_entity_to_sensor(entity)
                
                if sensor.temperature and sensor.temperature > ALERT_THRESHOLD_TEMP:
                    alert_key = f"{sensor.device_id}_temp"
                    if alert_key not in last_alert_sent:
                        await websocket.send_json({
                            "type": "alert",
                            "severity": "warning",
                            "device_id": sensor.device_id,
                            "message": f"Nhiệt độ cao: {sensor.temperature}°C",
                            "timestamp": datetime.now().isoformat()
                        })
                        last_alert_sent[alert_key] = datetime.now()
                
                if sensor.smokeLevel and sensor.smokeLevel > ALERT_THRESHOLD_SMOKE:
                    alert_key = f"{sensor.device_id}_smoke"
                    if alert_key not in last_alert_sent:
                        await websocket.send_json({
                            "type": "alert",
                            "severity": "critical",
                            "device_id": sensor.device_id,
                            "message": f"Phát hiện khói: {sensor.smokeLevel}ppm",
                            "timestamp": datetime.now().isoformat()
                        })
                        last_alert_sent[alert_key] = datetime.now()
            
            await asyncio.sleep(WEBSOCKET_BROADCAST_INTERVAL)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)