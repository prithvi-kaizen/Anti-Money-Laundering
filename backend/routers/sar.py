"""
Sentinel AML — SAR Router
"""

from fastapi import APIRouter, HTTPException
from services.rag_pipeline import generate_sar
from services.data_ingestion import get_alert_by_id

router = APIRouter(prefix="/alerts", tags=["sar"])


@router.post("/{alert_id}/sar")
def generate_sar_report(alert_id: str):
    """Generate a Suspicious Activity Report for an alert."""
    alert = get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    sar = generate_sar(alert_id)
    if not sar:
        raise HTTPException(status_code=500, detail="Failed to generate SAR")
    return sar
