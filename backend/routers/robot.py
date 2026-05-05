from fastapi import APIRouter
from pydantic import BaseModel
import httpx
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

ORION_URL = os.getenv("ORION_URL", "http://localhost:1026/v2")

class NavigateRequest(BaseModel):
    target_zone: str

class AnnounceRequest(BaseModel):
    message: str

class ControlRequest(BaseModel):
    device_id: str
    command: str
    value: str | bool

@router.post("/navigate")
async def robot_navigate(request: NavigateRequest):
    """Simulate sending a navigation command to Cruzr Robot."""
    # In a real scenario, this would call the Robot's internal REST/ROS API
    logger.info(f"CRUZR ROBOT: Navigating to {request.target_zone}")
    print(f"\n🤖 [CRUZR ROBOT] Moving to: {request.target_zone}\n")
    return {"status": "success", "action": "navigate", "target": request.target_zone}

@router.post("/announce")
async def robot_announce(request: AnnounceRequest):
    """Simulate sending a voice announcement command to Cruzr Robot."""
    logger.info(f"CRUZR ROBOT Announcement: {request.message}")
    print(f"\n🔊 [CRUZR ROBOT TTS]: {request.message}\n")
    return {"status": "success", "action": "announce", "message": request.message}

@router.post("/matter/control")
async def robot_matter_control(request: ControlRequest):
    """
    Relay a Matter device control command.
    Updates the Orion entity, which in turn would trigger the FIWARE IoT Agent (Matter).
    """
    logger.info(f"MATTER RELAY: Controlling {request.device_id} - {request.command}={request.value}")
    
    # We update the entity in Orion to simulate the command
    # FIWARE Orion uses PATCH /v2/entities/{id}/attrs to update attributes
    entity_id = request.device_id
    if not entity_id.startswith("urn:ngsi-ld:"):
        entity_id = f"urn:ngsi-ld:SmartPlug:{request.device_id}"
        
    payload = {
        request.command: {
            "type": "Boolean" if isinstance(request.value, bool) else "Text",
            "value": request.value
        }
    }
    
    headers = {
        "fiware-service": "cruzrtwin",
        "fiware-servicepath": "/",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                f"{ORION_URL}/entities/{entity_id}/attrs",
                json=payload,
                headers=headers
            )
            # Accept 204 No Content
            if response.status_code in (204, 200):
                print(f"\n🔌 [MATTER RELAY] Device {entity_id} {request.command} set to {request.value}\n")
                return {"status": "success", "device": entity_id, "state": request.value}
            else:
                return {"status": "error", "message": f"Orion returned {response.status_code}", "detail": response.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}
