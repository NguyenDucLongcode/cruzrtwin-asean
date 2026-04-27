
from fastapi import APIRouter, Request
from services.alert_service import process_anomaly_alert

# Webhook endpoint nhận alert từ FIWARE subscription
router = APIRouter(prefix="/api/webhook", tags=["Webhook"])

# Endpoint để nhận alert từ FIWARE subscription
@router.post("/anomaly")
async def anomaly_webhook(request: Request):
    """
    Webhook endpoint nhận alert từ FIWARE subscription
    Alert fires within 2s of anomaly injection
    """
    try:
        payload = await request.json()
        
       # Xử lý alert và gửi đến dashboard + robot
        alerts = await process_anomaly_alert(payload)
        forwarded_count = sum(1 for item in alerts if item.get("robot_forwarded"))

        return {
            "status": "ok",
            "message": "Alert received",
            "processed": len(alerts),
            "forwarded": forwarded_count,
        }
        
    except Exception as e:
        print(f"  Webhook error: {e}")
        return {"status": "error", "message": str(e)}