"""
Sentinel AML — Audit Router
"""

from fastapi import APIRouter, HTTPException
from services.audit_logger import get_audit_trail
from services.data_ingestion import get_alert_by_id

router = APIRouter(prefix="/alerts", tags=["audit"])


@router.get("/{alert_id}/audit")
def get_audit(alert_id: str):
    """Get audit trail for an alert investigation."""
    alert = get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    trail = get_audit_trail(alert_id)
    return trail
