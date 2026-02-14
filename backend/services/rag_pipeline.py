"""
Sentinel AML — RAG Pipeline & SAR Generator
Vector-indexed evidence retrieval + deterministic SAR generation.
"""

import uuid
import time
from datetime import datetime, timezone
from services.data_ingestion import (
    get_alert_by_id, get_entity_by_id,
    get_transactions_by_ids, get_transactions_for_entity,
    get_accounts_for_entity, check_sanctions
)
from services.risk_engine import analyze_risk
from services.audit_logger import log_action

# Simple in-memory text similarity (TF-IDF style) for MVP
# Avoids heavy sentence-transformers + FAISS dependency for faster startup
_evidence_index: dict[str, dict] = {}
_indexed = False


def _tokenize(text: str) -> set[str]:
    """Simple tokenization for text matching."""
    return set(text.lower().split())


def build_evidence_index(transactions: list[dict]):
    """Build a simple inverted index from transactions."""
    global _evidence_index, _indexed
    for tx in transactions:
        desc = tx.get("description", "")
        tokens = _tokenize(desc)
        _evidence_index[tx["tx_id"]] = {
            "tx_id": tx["tx_id"],
            "description": desc,
            "tokens": tokens,
            "amount": tx["amount"],
            "date": tx["date"],
            "sender": tx["sender_name"],
            "receiver": tx["receiver_name"],
            "pattern": tx.get("suspicious_pattern"),
        }
    _indexed = True


def retrieve_evidence(query: str, top_k: int = 10) -> list[dict]:
    """Retrieve top-k most relevant evidence entries."""
    query_tokens = _tokenize(query)
    scored = []
    for tx_id, entry in _evidence_index.items():
        overlap = len(query_tokens & entry["tokens"])
        if overlap > 0:
            # Boost suspicious transactions
            boost = 2.0 if entry["pattern"] else 1.0
            scored.append((overlap * boost, entry))
    scored.sort(key=lambda x: -x[0])
    return [e for _, e in scored[:top_k]]


def generate_sar(alert_id: str) -> dict:
    """Generate a structured SAR report for the given alert."""
    start = time.time()
    alert = get_alert_by_id(alert_id)
    if not alert:
        return None

    entity = get_entity_by_id(alert["entity_id"])
    related_txs = get_transactions_by_ids(alert.get("related_transactions", []))
    all_entity_txs = get_transactions_for_entity(alert["entity_id"])
    accounts = get_accounts_for_entity(alert["entity_id"])
    sanctions = check_sanctions(
        alert.get("entity_name", ""),
        entity.get("country", "") if entity else ""
    )
    risk = analyze_risk(alert_id)

    # Log data retrieval
    log_action(alert_id, "DATA_RETRIEVAL", "rag_pipeline",
               f"Retrieving data for alert {alert_id}",
               f"Retrieved {len(related_txs)} related transactions, "
               f"{len(all_entity_txs)} entity transactions, "
               f"{len(accounts)} accounts, {len(sanctions)} sanctions matches",
               evidence_ids=[t["tx_id"] for t in related_txs[:5]],
               duration_ms=int((time.time() - start) * 1000))

    # Retrieve contextual evidence
    query = f"{alert.get('entity_name', '')} {alert.get('trigger_pattern', '')} suspicious"
    evidence_results = retrieve_evidence(query, top_k=10)

    log_action(alert_id, "EVIDENCE_RETRIEVAL", "rag_pipeline",
               f"Querying evidence index: '{query}'",
               f"Retrieved {len(evidence_results)} relevant evidence entries",
               evidence_ids=[e["tx_id"] for e in evidence_results[:5]])

    # Build SAR
    sar_id = f"SAR-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now(timezone.utc).isoformat()

    # 1. Case Overview
    case_overview = _build_case_overview(alert, entity, risk, sanctions)

    # 2. Timeline
    timeline = _build_timeline(all_entity_txs, related_txs)

    # 3. Risk Indicators
    risk_indicators = risk.get("drivers", [])

    # 4. Linked Entities
    linked_entities = _build_linked_entities(all_entity_txs, entity)

    # 5. Evidence Citations
    evidence_citations = _build_evidence_citations(
        related_txs, all_entity_txs, sanctions, risk
    )

    # 6. Recommended Action
    recommended_action = _build_recommendation(risk, sanctions, alert)

    sar = {
        "sar_id": sar_id,
        "alert_id": alert_id,
        "generated_at": now,
        "case_overview": case_overview,
        "timeline": timeline,
        "risk_indicators": risk_indicators,
        "linked_entities": linked_entities,
        "evidence_citations": evidence_citations,
        "recommended_action": recommended_action,
        "overall_risk_score": risk["risk_score"],
        "overall_confidence": risk["confidence"],
    }

    log_action(alert_id, "SAR_GENERATION", "rag_pipeline",
               f"Generating SAR {sar_id} for alert {alert_id}",
               f"SAR generated with {len(risk_indicators)} risk indicators, "
               f"{len(evidence_citations)} citations, {len(linked_entities)} linked entities",
               evidence_ids=[e["evidence_id"] for e in evidence_citations[:5]],
               duration_ms=int((time.time() - start) * 1000))

    return sar


def _build_case_overview(alert, entity, risk, sanctions):
    entity_name = alert.get("entity_name", "Unknown")
    entity_type = entity.get("type", "Unknown") if entity else "Unknown"
    country = entity.get("country", "Unknown") if entity else "Unknown"
    trigger = alert.get("trigger_pattern", "").replace("_", " ")

    sanctions_note = ""
    if sanctions:
        programs = ", ".join(set(s["program"] for s in sanctions))
        sanctions_note = f" The entity has been identified with proximity to sanctions lists ({programs})."

    return (
        f"This Suspicious Activity Report pertains to {entity_name}, "
        f"a {entity_type.lower().replace('_', ' ')} entity based in {country}. "
        f"The investigation was triggered by a {trigger} pattern detected in transaction monitoring. "
        f"The overall risk assessment is {risk['risk_level']} with a confidence score of "
        f"{risk['confidence']:.0%}. {len(risk.get('drivers', []))} distinct risk indicators "
        f"were identified during the analysis.{sanctions_note}"
    )


def _build_timeline(all_txs, related_txs):
    timeline = []
    related_ids = {t["tx_id"] for t in related_txs}

    sorted_txs = sorted(all_txs, key=lambda t: t["date"])
    for tx in sorted_txs[:20]:  # Limit to 20 entries
        timeline.append({
            "date": tx["date"],
            "tx_id": tx["tx_id"],
            "event": f"{tx['tx_type']}: ${tx['amount']:,.2f} "
                     f"from {tx['sender_name']} to {tx['receiver_name']}",
            "amount": tx["amount"],
            "flagged": tx["tx_id"] in related_ids or tx.get("suspicious_pattern") is not None,
            "pattern": tx.get("suspicious_pattern"),
        })
    return timeline


def _build_linked_entities(all_txs, primary_entity):
    entity_map = {}
    primary_id = primary_entity["entity_id"] if primary_entity else ""

    for tx in all_txs:
        for role, eid, name, country in [
            ("sender", tx["sender_entity"], tx["sender_name"], tx.get("sender_country", "")),
            ("receiver", tx["receiver_entity"], tx["receiver_name"], tx.get("receiver_country", "")),
        ]:
            if eid != primary_id and eid not in entity_map:
                entity_map[eid] = {
                    "entity_id": eid,
                    "name": name,
                    "country": country,
                    "relationship": role,
                    "transaction_count": 0,
                    "total_amount": 0,
                }
            if eid != primary_id:
                entity_map[eid]["transaction_count"] += 1
                entity_map[eid]["total_amount"] += tx["amount"]

    linked = sorted(entity_map.values(), key=lambda x: -x["total_amount"])
    return linked[:15]


def _build_evidence_citations(related_txs, all_txs, sanctions, risk):
    citations = []
    cite_counter = 1

    # Transaction evidence
    for tx in related_txs[:8]:
        citations.append({
            "evidence_id": f"EV-{cite_counter:03d}",
            "type": "transaction",
            "description": tx.get("description", f"Transaction {tx['tx_id']}"),
            "source_ids": [tx["tx_id"]],
            "confidence": 0.9 if tx.get("suspicious_pattern") else 0.6,
        })
        cite_counter += 1

    # Pattern evidence
    patterns = {}
    for tx in all_txs:
        p = tx.get("suspicious_pattern")
        if p and p not in patterns:
            patterns[p] = []
        if p:
            patterns[p].append(tx["tx_id"])

    for pattern, tx_ids in patterns.items():
        citations.append({
            "evidence_id": f"EV-{cite_counter:03d}",
            "type": "pattern",
            "description": f"{pattern.replace('_', ' ').title()} pattern detected across "
                           f"{len(tx_ids)} transactions",
            "source_ids": tx_ids[:5],
            "confidence": 0.85,
        })
        cite_counter += 1

    # Sanctions evidence
    for s in sanctions[:3]:
        citations.append({
            "evidence_id": f"EV-{cite_counter:03d}",
            "type": "sanctions_match",
            "description": f"Sanctions list match: {s['name']} ({s['program']}) — {s['reason']}",
            "source_ids": [s["sanction_id"]],
            "confidence": 0.95,
        })
        cite_counter += 1

    return citations


def _build_recommendation(risk, sanctions, alert):
    risk_level = risk["risk_level"]
    n_drivers = len(risk.get("drivers", []))

    if risk_level == "CRITICAL":
        action = "IMMEDIATE ESCALATION"
        detail = ("This case requires immediate escalation to the BSA Officer and filing of a "
                  "Suspicious Activity Report with FinCEN within 30 days. ")
    elif risk_level == "HIGH":
        action = "ESCALATE FOR REVIEW"
        detail = ("This case should be escalated for senior analyst review. A SAR filing should be "
                  "considered based on additional investigation. ")
    elif risk_level == "MEDIUM":
        action = "ENHANCED MONITORING"
        detail = ("Place the account(s) under enhanced monitoring. Schedule follow-up review in 30 days. ")
    else:
        action = "CLOSE — FALSE POSITIVE"
        detail = "Insufficient evidence to support suspicious activity designation. "

    sanctions_note = ""
    if sanctions:
        sanctions_note = (f"Additional due diligence required due to sanctions proximity "
                          f"({len(sanctions)} match(es)). ")

    return (
        f"RECOMMENDED ACTION: {action}. {detail}{sanctions_note}"
        f"This determination is based on {n_drivers} identified risk driver(s) "
        f"with an overall confidence of {risk['confidence']:.0%}."
    )
