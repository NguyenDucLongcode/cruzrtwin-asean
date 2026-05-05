from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter()

ORION_URL = os.getenv("ORION_URL", "http://localhost:1026/v2")
FIWARE_SERVICE = "cruzrtwin"
FIWARE_SERVICEPATH = "/"

HEADERS = {
    "fiware-service": FIWARE_SERVICE,
    "fiware-servicepath": FIWARE_SERVICEPATH,
    "Accept": "application/json"
}

@router.get("/sensors")
async def get_sensors():
    """Fetch real-time sensor data from FIWARE Orion."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{ORION_URL}/entities",
                headers=HEADERS,
                params={"type": "TemperatureSensor,HumiditySensor,SmokeSensor,AirQualitySensor"}
            )
            response.raise_for_status()
            
            # Format data to be easily consumed by frontend
            raw_entities = response.json()
            sensors = []
            for entity in raw_entities:
                sensor_data = {
                    "id": entity["id"],
                    "type": entity["type"],
                }
                # Extract simple values
                for key, val in entity.items():
                    if key not in ("id", "type") and isinstance(val, dict) and "value" in val:
                        sensor_data[key] = val["value"]
                sensors.append(sensor_data)
                
            return {"status": "success", "data": sensors}
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Cannot connect to Orion: {exc}")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail="Error fetching data from Orion")

@router.get("/energy")
async def get_energy_stats():
    """Fetch energy statistics (SmartPlug data) from Orion."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{ORION_URL}/entities",
                headers=HEADERS,
                params={"type": "SmartPlug"}
            )
            response.raise_for_status()
            
            raw_entities = response.json()
            plugs = []
            for entity in raw_entities:
                plug_data = {
                    "id": entity["id"],
                    "type": entity["type"],
                }
                for key, val in entity.items():
                    if key not in ("id", "type") and isinstance(val, dict) and "value" in val:
                        plug_data[key] = val["value"]
                plugs.append(plug_data)
                
            return {"status": "success", "data": plugs}
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Cannot connect to Orion: {exc}")

@router.get("/alerts")
async def get_alerts():
    """Fetch recent RiskAlerts or Anomalies from Orion."""
    async with httpx.AsyncClient() as client:
        try:
            # We fetch entities of type RiskAlert
            response = await client.get(
                f"{ORION_URL}/entities",
                headers=HEADERS,
                params={"type": "RiskAlert"}
            )
            if response.status_code == 200:
                return {"status": "success", "data": response.json()}
            return {"status": "success", "data": []}
        except Exception:
            return {"status": "success", "data": []}
