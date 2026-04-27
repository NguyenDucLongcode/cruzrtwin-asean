from fastapi import APIRouter
from datetime import datetime
import requests
from config import FIWARE_ORION_URL

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    """
    Health check endpoint for demo reliability
    Kiểm tra kết nối FIWARE và trạng thái service
    """
    # Kiểm tra FIWARE Orion
    orion_status = "down"
    try:
        base_url = FIWARE_ORION_URL.rsplit("/v2", 1)[0]
        response = requests.get(f"{base_url}/version", timeout=2)
        if response.status_code == 200:
            orion_status = "up"
    except:
        pass
    
    return {
        "status": "healthy",
        "service": "backend-api",
        "version": "1.0.0",
        "orion": orion_status,
        "timestamp": datetime.now().isoformat()
    }