from fastapi import APIRouter, HTTPException
from services.data_ingestion import DataIngestion
from services.ai_investigator import AIInvestigator
from services.entity_extraction import GraphBuilder
from services.audit_logger import AuditLogger
import time

router = APIRouter(prefix="/alerts", tags=["alerts"])
db = DataIngestion()
ai = AIInvestigator()
gb = GraphBuilder()
audit = AuditLogger()

@router.get("")
def list_alerts():
    alerts = db.get_all_alerts()
    # Sort strictly by severity
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    sorted_alerts = sorted([a.model_dump() for a in alerts], key=lambda x: severity_order.get(x["severity"], 4))
    return sorted_alerts

@router.get("/{alert_id}")
def get_alert_detail(alert_id: str):
    alert = db.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404)
    entity = db.get_entity(alert.entity_id)
    txs = db.get_related_transactions(alert.entity_id)
    return {
        "alert": alert.model_dump(),
        "entity": entity.model_dump() if entity else None,
        "transactions": [t.model_dump() for t in txs]
    }

@router.post("/{alert_id}/investigate")
def investigate_alert(alert_id: str):
    start = time.time()
    alert = db.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404)
    entity = db.get_entity(alert.entity_id)
    txs = db.get_related_transactions(alert.entity_id)
    all_ents = db.get_all_scenario_entities(alert.entity_id)
    graph = gb.build_from_transactions([e.model_dump() for e in all_ents], [t.model_dump() for t in txs])
    
    result = ai.investigate(alert.model_dump(), entity, txs, graph)
    duration = int((time.time() - start) * 1000)
    
    # Audit log
    rec = result["ai_analysis"].get("sar_recommendation", "UNKNOWN")
    audit.log_event(
        alert_id=alert_id,
        step="ai_investigation",
        actor="ai_agent",
        decision=rec,
        confidence=result["confidence_score"],
        citations=result["ai_analysis"].get("typologies_identified", []),
        duration_ms=duration,
        input_data={"alert_id": alert_id},
        output_data=result
    )
    
    if result.get("guardrail_overrides"):
        for override in result["guardrail_overrides"]:
            audit.log_event(
                alert_id=alert_id,
                step="guardrail_override",
                actor="compliance_engine",
                decision="MANDATORY_SAR_OVERRIDE",
                confidence=1.0,
                citations=override.get("regulatory_basis", []),
                duration_ms=0,
                input_data={"ai_rec": rec},
                output_data={"override": override}
            )
        
    return result
