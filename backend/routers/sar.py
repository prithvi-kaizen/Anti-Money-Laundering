from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from services.data_ingestion import DataIngestion
from services.ai_investigator import AIInvestigator
from services.sar_generator import SARGenerator
from services.entity_extraction import GraphBuilder

router = APIRouter(prefix="/alerts/{alert_id}", tags=["sar"])
db = DataIngestion()
ai = AIInvestigator()
sar_gen = SARGenerator()
gb = GraphBuilder()

@router.get("/investigate/stream")
async def stream_sar(alert_id: str):
    alert = db.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404)
    entity = db.get_entity(alert.entity_id)
    txs = db.get_related_transactions(alert.entity_id)
    all_ents = db.get_all_scenario_entities(alert.entity_id)
    graph = gb.build_from_transactions([e.model_dump() for e in all_ents], [t.model_dump() for t in txs])
    
    # We do a quick investigate run here to feed the generator.
    # In a real system, you might cache the investigate result or do it async in one step.
    inv_result = ai.investigate(alert.model_dump(), entity, txs, graph)
    return StreamingResponse(sar_gen.generate_sar_stream(inv_result, entity, txs), media_type="text/event-stream")
