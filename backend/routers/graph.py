"""
Sentinel AML — Graph Router
"""

from fastapi import APIRouter, HTTPException
from services.entity_extraction import build_entity_graph
from services.data_ingestion import get_alert_by_id

router = APIRouter(prefix="/alerts", tags=["graph"])


@router.get("/{alert_id}/graph")
def get_entity_graph(alert_id: str):
    """Get entity relationship graph for an alert."""
    alert = get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    graph = build_entity_graph(alert_id)
    return graph
