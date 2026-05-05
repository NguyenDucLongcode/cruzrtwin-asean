from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from typing import List
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Basic WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@router.post("/fiware")
async def fiware_webhook(request: Request):
    """
    Webhook to receive notifications from FIWARE Orion subscriptions.
    When Orion detects a condition (e.g. RiskAlert created, or Anomaly), it POSTs here.
    """
    try:
        body = await request.json()
        logger.info(f"Received Webhook from FIWARE: {json.dumps(body)}")
        
        # Typically FIWARE sends a payload like:
        # {
        #   "subscriptionId": "...",
        #   "data": [
        #       { "id": "...", "type": "RiskAlert", "riskLevel": {"value": "HIGH"}, ... }
        #   ]
        # }
        
        if "data" in body:
            entities = body["data"]
            for entity in entities:
                print(f"\n🚨 [WEBHOOK ALERT] Received update for: {entity.get('id', 'Unknown')}\n")
                
                # Broadcast the entity update to all connected WebSockets (Dashboard)
                message = json.dumps({
                    "event": "alert",
                    "entity": entity
                })
                await manager.broadcast(message)
                
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket endpoint for the Dashboard to subscribe to real-time alerts.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, wait for client messages if any
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
