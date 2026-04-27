from fastapi import APIRouter, Query

from services.alert_service import get_recent_alerts, get_latest_alert

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("/")
def list_alerts(limit: int = Query(default=20, ge=1, le=200)):
	"""Trả về danh sách alert gần nhất cho dashboard."""
	items = get_recent_alerts(limit=limit)
	return {
		"total": len(items),
		"items": items,
	}


@router.get("/latest")
def latest_alert():
	"""Trả về alert mới nhất nếu có."""
	item = get_latest_alert()
	return {
		"has_alert": item is not None,
		"item": item,
	}
