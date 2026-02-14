"""
Sentinel AML — FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.data_ingestion import load_all_data, get_transactions
from services.rag_pipeline import build_evidence_index
from routers import alerts, graph, sar, audit, timing

app = FastAPI(
    title="Sentinel AML Investigator",
    description="GenAI-powered AML co-investigator API",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(alerts.router)
app.include_router(graph.router)
app.include_router(sar.router)
app.include_router(audit.router)
app.include_router(timing.router)


@app.on_event("startup")
def startup_event():
    """Load data and build indexes on startup."""
    print("🚀 Starting Sentinel AML backend...")
    load_all_data()
    transactions = get_transactions()
    build_evidence_index(transactions)
    print("✅ All systems ready!")


@app.get("/")
def root():
    return {
        "name": "Sentinel AML Investigator",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "alerts": "/alerts",
            "alert_detail": "/alerts/{alert_id}",
            "investigate": "/alerts/{alert_id}/investigate",
            "graph": "/alerts/{alert_id}/graph",
            "sar": "/alerts/{alert_id}/sar",
            "audit": "/alerts/{alert_id}/audit",
            "timing": "/timing",
        },
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
