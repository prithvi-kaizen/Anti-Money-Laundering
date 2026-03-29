from dotenv import load_dotenv
load_dotenv()  # Must be first — loads backend/.env before any service imports read os.getenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import alerts, graph, sar, audit, metrics
from database import Base, engine

# Create the SQLite tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sentinel v2 API", description="AML Investigation Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alerts.router)
app.include_router(graph.router)
app.include_router(sar.router)
app.include_router(audit.router)
app.include_router(metrics.router)

@app.get("/compliance/config")
def get_compliance_config():
    from config import FATF_HIGH_RISK, FINCEN_CTR_THRESHOLD
    return {
        "fatf_high_risk": list(FATF_HIGH_RISK),
        "fincen_ctr_threshold": FINCEN_CTR_THRESHOLD
    }
