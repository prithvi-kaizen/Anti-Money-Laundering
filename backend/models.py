from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class Transaction(BaseModel):
    id: str
    source_id: str
    target_id: str
    amount: float
    currency: str = "USD"
    date: str
    type: str # e.g., "wire", "cash", "crypto"
    purpose: Optional[str] = None

class Entity(BaseModel):
    id: str
    name: str
    type: str # "person", "company", "account", "jurisdiction"
    jurisdiction: str
    risk_score: Optional[float] = None
    is_shell_suspect: bool = False
    attributes: Dict[str, Any] = Field(default_factory=dict)

class Alert(BaseModel):
    id: str
    entity_id: str
    rule_triggered: str
    timestamp: str
    severity: str # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    status: str = "OPEN" # OPEN, CLOSED, ESCALATED

class ComplianceFlag(BaseModel):
    rule_id: str
    severity: str          # CRITICAL | HIGH | MEDIUM | LOW
    description: str
    regulatory_citation: str
    evidence: dict         # specific transaction IDs, amounts, timestamps
    requires_sar: bool
