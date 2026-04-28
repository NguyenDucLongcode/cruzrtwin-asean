from fastapi import APIRouter, Request
from datetime import datetime
import logging

from services.alert_service import process_anomaly_alert
from api.energy import process_livingroom_data  # QUAN TRỌNG

router = APIRouter(prefix="/api/webhook", tags=["Webhook"])
logger = logging.getLogger(__name__)



# ============================================================
# ANOMALY WEBHOOK (AI)
# ============================================================
@router.post("/anomaly")
async def anomaly_webhook(request: Request):
    try:
        payload = await request.json()

        alerts = await process_anomaly_alert(payload)
        forwarded_count = sum(1 for item in alerts if item.get("robot_forwarded"))
       
        return {
            "status": "ok",
            "message": "Alert received",
            "processed": len(alerts),
            "forwarded": forwarded_count,
        }

    except Exception as e:
        logger.exception("Webhook anomaly error")
        return {"status": "error", "message": str(e)}


# ============================================================
# LIVING ROOM WEBHOOK (ENERGY)
# ============================================================

@router.post("/livingroom")
async def livingroom_webhook(request: Request):
    try:
        payload = await request.json()
        
        print("\n" + "="*60)
        print("🏠 LIVING ROOM WEBHOOK")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)

        # GỌI SERVICE XỬ LÝ
        result = await process_livingroom_data(payload)

        return {
            "status": "ok",
            "message": "Living room processed",
            "processed": result.get("processed", 0),
            "devices_tracked": result.get("devices_tracked", 0)
        }

    except Exception as e:
        logger.exception("Webhook livingroom error")
        return {"status": "error", "message": str(e)}