from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from datetime import datetime
from database import Base, SessionLocal
import hashlib
import json

class AuditEvent(Base):
    __tablename__ = "audit_trail"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    step = Column(String)           # "compliance_check" | "ai_investigation" | "sar_generation" | "guardrail_override"
    actor = Column(String)          # "compliance_engine" | "ai_agent" | "guardrail"
    decision = Column(String)
    confidence = Column(Float)
    regulatory_citations = Column(JSON)
    duration_ms = Column(Integer)
    input_hash = Column(String)     # SHA-256 of input for tamper detection
    output_hash = Column(String)    # SHA-256 of output for tamper detection

class AuditLogger:
    def __init__(self):
        # We assume standard scoped sessions for real use, but simple local usage here.
        pass
        
    def get_db(self):
        return SessionLocal()
        
    def _hash_data(self, data) -> str:
        return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()

    def log_event(self, alert_id: str, step: str, actor: str, decision: str, 
                  confidence: float, citations: list, duration_ms: int, 
                  input_data: dict, output_data: dict):
        db = self.get_db()
        try:
            event = AuditEvent(
                alert_id=alert_id,
                step=step,
                actor=actor,
                decision=decision,
                confidence=confidence,
                regulatory_citations=citations,
                duration_ms=duration_ms,
                input_hash=self._hash_data(input_data),
                output_hash=self._hash_data(output_data)
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            return event
        finally:
            db.close()
    
    def get_audit_trail(self, alert_id: str):
        db = self.get_db()
        try:
            events = db.query(AuditEvent).filter(AuditEvent.alert_id == alert_id).order_by(AuditEvent.timestamp.asc()).all()
            # Convert to dict for easy json serialization
            return [{
                "id": e.id,
                "timestamp": e.timestamp.isoformat(),
                "step": e.step,
                "actor": e.actor,
                "decision": e.decision,
                "confidence": e.confidence,
                "regulatory_citations": e.regulatory_citations,
                "duration_ms": e.duration_ms,
                "input_hash": e.input_hash,
                "output_hash": e.output_hash
            } for e in events]
        finally:
            db.close()
