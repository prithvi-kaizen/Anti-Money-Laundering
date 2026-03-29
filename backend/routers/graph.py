from fastapi import APIRouter, HTTPException
from services.data_ingestion import DataIngestion
from services.entity_extraction import GraphBuilder

router = APIRouter(prefix="/alerts/{alert_id}/graph", tags=["graph"])
db = DataIngestion()
gb = GraphBuilder()

@router.get("")
def get_graph(alert_id: str):
    alert = db.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404)
    txs = db.get_related_transactions(alert.entity_id)
    ents = db.get_all_scenario_entities(alert.entity_id)
    return gb.build_from_transactions([e.model_dump() for e in ents], [t.model_dump() for t in txs])
