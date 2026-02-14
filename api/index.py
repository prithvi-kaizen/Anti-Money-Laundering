"""
Vercel Serverless Handler — wraps FastAPI backend for Vercel Python runtime.

Data is loaded at module level so it persists across warm invocations.
"""

import sys
import os

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
sys.path.insert(0, backend_dir)

# ── Load data at module level (cached across warm invocations) ──
from services.data_ingestion import load_all_data, get_transactions
from services.rag_pipeline import build_evidence_index

load_all_data()
build_evidence_index(get_transactions())

# ── Build the Vercel-specific FastAPI app ──
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import alerts, graph, sar, audit, timing

app = FastAPI(
    title="Sentinel AML Investigator",
    description="GenAI-powered AML co-investigator",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers under /api prefix (Vercel routes /api/* here)
app.include_router(alerts.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(sar.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(timing.router, prefix="/api")


@app.get("/api")
@app.get("/api/health")
def health():
    return {"status": "healthy", "name": "Sentinel AML Investigator"}
