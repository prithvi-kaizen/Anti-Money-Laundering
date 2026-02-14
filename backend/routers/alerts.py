"""
Sentinel AML — Alert Router
"""

from fastapi import APIRouter, HTTPException
from services.data_ingestion import get_alerts, get_alert_by_id, get_transactions_by_ids, update_alert_status
from services.entity_extraction import build_entity_graph
from services.rag_pipeline import generate_sar
from services.risk_engine import analyze_risk
from services.audit_logger import log_action, get_audit_trail

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
def list_alerts(risk_level: str = None, status: str = None):
    """List all alerts with optional filtering."""
    alerts = get_alerts()
    if risk_level:
        alerts = [a for a in alerts if a["risk_level"] == risk_level.upper()]
    if status:
        alerts = [a for a in alerts if a["status"] == status.upper()]
    return {
        "alerts": alerts,
        "total": len(alerts),
    }


@router.get("/{alert_id}")
def get_alert(alert_id: str):
    """Get detailed alert information."""
    alert = get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    # Include full transaction details
    txs = get_transactions_by_ids(alert.get("related_transactions", []))
    return {**alert, "transactions": txs}


@router.post("/{alert_id}/investigate")
def investigate_alert(alert_id: str):
    """Trigger full investigation for an alert — generates SAR, graph, risk analysis, audit trail."""
    alert = get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    # Update status
    update_alert_status(alert_id, "UNDER_REVIEW")

    # Log investigation start
    log_action(alert_id, "INVESTIGATION_START", "alert_router",
               f"Investigation initiated for alert {alert_id}",
               f"Alert entity: {alert['entity_name']}, Risk: {alert['risk_level']}")

    # Generate all components
    graph = build_entity_graph(alert_id)
    log_action(alert_id, "GRAPH_BUILT", "entity_extraction",
               f"Building entity graph for {alert_id}",
               f"Graph contains {len(graph['nodes'])} nodes and {len(graph['edges'])} edges",
               evidence_ids=[n["id"] for n in graph["nodes"][:5]])

    risk = analyze_risk(alert_id)
    log_action(alert_id, "RISK_ANALYZED", "risk_engine",
               f"Analyzing risk for {alert_id}",
               f"Risk level: {risk['risk_level']}, Score: {risk['risk_score']}, "
               f"{len(risk['drivers'])} drivers identified",
               evidence_ids=[d["evidence_ids"][0] for d in risk["drivers"] if d["evidence_ids"]])

    sar = generate_sar(alert_id)

    log_action(alert_id, "INVESTIGATION_COMPLETE", "alert_router",
               f"Investigation completed for {alert_id}",
               f"SAR {sar['sar_id'] if sar else 'N/A'} generated. "
               f"Risk: {risk['risk_level']}")

    audit = get_audit_trail(alert_id)

    return {
        "alert_id": alert_id,
        "sar": sar,
        "risk_explanation": risk,
        "graph": graph,
        "audit_trail": audit,
    }
