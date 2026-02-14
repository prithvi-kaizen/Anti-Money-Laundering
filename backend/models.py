"""
Sentinel AML — Pydantic Models
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    NEW = "NEW"
    UNDER_REVIEW = "UNDER_REVIEW"
    ESCALATED = "ESCALATED"
    CLOSED_SUSPICIOUS = "CLOSED_SUSPICIOUS"
    CLOSED_FALSE_POSITIVE = "CLOSED_FALSE_POSITIVE"


class TransactionResponse(BaseModel):
    tx_id: str
    date: str
    sender_account: str
    sender_entity: str
    sender_name: str
    receiver_account: str
    receiver_entity: str
    receiver_name: str
    amount: float
    currency: str
    tx_type: str
    sender_country: str
    receiver_country: str
    suspicious_pattern: Optional[str] = None
    description: str


class AlertSummary(BaseModel):
    alert_id: str
    entity_id: str
    entity_name: str
    entity_type: str
    country: str
    risk_score: int
    risk_level: RiskLevel
    trigger_pattern: str
    status: AlertStatus
    created_date: str
    summary: str


class AlertDetail(AlertSummary):
    trigger_tx: str
    related_transactions: list[str]
    sanctions_match: bool
    assigned_to: Optional[str] = None
    transactions: list[TransactionResponse] = []


class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # "entity", "account", "transaction"
    risk: bool = False
    country: Optional[str] = None
    metadata: dict = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    label: str
    amount: Optional[float] = None
    tx_id: Optional[str] = None


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    alert_id: str


class EvidenceCitation(BaseModel):
    evidence_id: str
    type: str  # "transaction", "entity_link", "sanctions_match", "pattern"
    description: str
    source_ids: list[str]
    confidence: float = Field(ge=0.0, le=1.0)


class RiskIndicator(BaseModel):
    indicator: str
    severity: RiskLevel
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: list[str]
    description: str


class SARReport(BaseModel):
    sar_id: str
    alert_id: str
    generated_at: str
    case_overview: str
    timeline: list[dict]
    risk_indicators: list[RiskIndicator]
    linked_entities: list[dict]
    evidence_citations: list[EvidenceCitation]
    recommended_action: str
    overall_risk_score: int
    overall_confidence: float = Field(ge=0.0, le=1.0)


class AuditEntry(BaseModel):
    entry_id: str
    alert_id: str
    timestamp: str
    action: str
    module: str
    input_summary: str
    output_summary: str
    evidence_ids: list[str] = []
    duration_ms: int = 0


class AuditTrail(BaseModel):
    alert_id: str
    entries: list[AuditEntry]
    total_duration_ms: int


class RiskExplanation(BaseModel):
    alert_id: str
    risk_score: int
    risk_level: RiskLevel
    confidence: float
    drivers: list[RiskIndicator]
    summary: str


class InvestigationResponse(BaseModel):
    alert_id: str
    sar: SARReport
    risk_explanation: RiskExplanation
    graph: GraphResponse
    audit_trail: AuditTrail


class TimingComparison(BaseModel):
    manual_avg_minutes: float
    sentinel_avg_minutes: float
    reduction_percent: float
    sample_size: int
