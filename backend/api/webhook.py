
from fastapi import APIRouter, Request, BackgroundTasks
from services.alert_service import process_anomaly_alert

# Webhook endpoint nhận alert từ FIWARE subscription
router = APIRouter(prefix="/api/webhook", tags=["Webhook"])

@router.post("/anomaly")
async def anomaly_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint nhận alert từ FIWARE subscription
    Alert fires within 2s of anomaly injection
    """
    try:
        payload = await request.json()
        
        # Xử lý alert trong background (không block response)
        background_tasks.add_task(process_anomaly_alert, payload)
        
        return {"status": "ok", "message": "Alert received"}
        
    except Exception as e:
        print(f"   ❌ Webhook error: {e}")
        return {"status": "error", "message": str(e)}