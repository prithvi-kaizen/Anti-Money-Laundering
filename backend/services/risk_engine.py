"""
Sentinel AML — Risk Engine
Rule-based risk scoring with confidence and driver explanations.
"""

from services.data_ingestion import (
    get_alert_by_id, get_entity_by_id,
    get_transactions_by_ids, get_transactions_for_entity,
    check_sanctions
)


STRUCTURING_THRESHOLD = 10000
RAPID_MOVEMENT_HOURS = 48
HIGH_RISK_COUNTRIES = {"KY", "PA", "BS", "RU", "NG", "IR"}


def analyze_risk(alert_id: str) -> dict:
    """Perform comprehensive risk analysis for an alert."""
    alert = get_alert_by_id(alert_id)
    if not alert:
        return _empty_risk(alert_id)

    entity = get_entity_by_id(alert["entity_id"])
    related_txs = get_transactions_by_ids(alert.get("related_transactions", []))
    all_entity_txs = get_transactions_for_entity(alert["entity_id"])

    drivers = []
    driver_boost = 0
    alert_base_score = alert.get("risk_score", 50)
    alert_base_level = alert.get("risk_level", "MEDIUM")

    # 1. Structuring detection
    structuring_txs = [t for t in all_entity_txs
                       if t.get("suspicious_pattern") == "structuring"
                       or (t["amount"] >= 8000 and t["amount"] < STRUCTURING_THRESHOLD)]
    if structuring_txs:
        confidence = min(len(structuring_txs) * 0.2, 1.0)
        driver_boost += 5
        drivers.append({
            "indicator": "Structuring Pattern Detected",
            "severity": "HIGH",
            "confidence": round(confidence, 2),
            "evidence_ids": [t["tx_id"] for t in structuring_txs[:5]],
            "description": f"{len(structuring_txs)} transactions detected just below "
                           f"${STRUCTURING_THRESHOLD:,} reporting threshold. "
                           f"Amounts range from ${min(t['amount'] for t in structuring_txs):,.2f} "
                           f"to ${max(t['amount'] for t in structuring_txs):,.2f}.",
        })

    # 2. Sanctions proximity
    sanctions_matches = []
    if entity:
        sanctions_matches = check_sanctions(entity["name"], entity["country"])
    if sanctions_matches:
        confidence = 0.9
        driver_boost += 8
        drivers.append({
            "indicator": "Sanctions List Proximity",
            "severity": "CRITICAL",
            "confidence": confidence,
            "evidence_ids": [s["sanction_id"] for s in sanctions_matches[:3]],
            "description": f"Entity or jurisdiction matches {len(sanctions_matches)} "
                           f"sanctions list entries. Programs: "
                           f"{', '.join(set(s['program'] for s in sanctions_matches))}.",
        })

    # 3. High-risk country involvement
    hr_txs = [t for t in all_entity_txs
              if t.get("sender_country") in HIGH_RISK_COUNTRIES
              or t.get("receiver_country") in HIGH_RISK_COUNTRIES]
    if hr_txs:
        confidence = min(len(hr_txs) * 0.15, 0.95)
        driver_boost += 3
        countries = set()
        for t in hr_txs:
            if t.get("sender_country") in HIGH_RISK_COUNTRIES:
                countries.add(t["sender_country"])
            if t.get("receiver_country") in HIGH_RISK_COUNTRIES:
                countries.add(t["receiver_country"])
        drivers.append({
            "indicator": "High-Risk Jurisdiction Activity",
            "severity": "HIGH",
            "confidence": round(confidence, 2),
            "evidence_ids": [t["tx_id"] for t in hr_txs[:5]],
            "description": f"{len(hr_txs)} transactions involving high-risk jurisdictions: "
                           f"{', '.join(countries)}.",
        })

    # 4. Rapid movement
    rapid_txs = [t for t in all_entity_txs if t.get("suspicious_pattern") == "rapid_movement"]
    if rapid_txs:
        total_amount = sum(t["amount"] for t in rapid_txs)
        confidence = min(0.6 + len(rapid_txs) * 0.1, 0.95)
        driver_boost += 4
        drivers.append({
            "indicator": "Rapid Fund Movement",
            "severity": "HIGH",
            "confidence": round(confidence, 2),
            "evidence_ids": [t["tx_id"] for t in rapid_txs[:5]],
            "description": f"${total_amount:,.2f} moved rapidly across {len(rapid_txs)} "
                           f"transactions. Funds transferred within {RAPID_MOVEMENT_HOURS} hours.",
        })

    # 5. Round-trip detection
    roundtrip_txs = [t for t in all_entity_txs if t.get("suspicious_pattern") == "round_trip"]
    if roundtrip_txs:
        total_amount = sum(t["amount"] for t in roundtrip_txs)
        driver_boost += 6
        drivers.append({
            "indicator": "Round-Trip Transaction Pattern",
            "severity": "CRITICAL",
            "confidence": 0.85,
            "evidence_ids": [t["tx_id"] for t in roundtrip_txs[:5]],
            "description": f"${total_amount:,.2f} in round-trip transactions detected. "
                           f"Funds routed through intermediaries and returned to origin.",
        })

    # 6. Shell company involvement
    if entity and entity.get("type") == "SHELL_COMPANY":
        driver_boost += 3
        drivers.append({
            "indicator": "Shell Company Involvement",
            "severity": "MEDIUM",
            "confidence": 0.7,
            "evidence_ids": [entity["entity_id"]],
            "description": f"Primary entity '{entity['name']}' is classified as a shell company "
                           f"registered in {entity.get('country', 'unknown jurisdiction')}.",
        })

    # 7. High transaction volume
    if len(all_entity_txs) > 20:
        driver_boost += 2
        total_amount = sum(t["amount"] for t in all_entity_txs)
        drivers.append({
            "indicator": "Unusually High Transaction Volume",
            "severity": "MEDIUM",
            "confidence": 0.6,
            "evidence_ids": [t["tx_id"] for t in all_entity_txs[:3]],
            "description": f"{len(all_entity_txs)} transactions totaling "
                           f"${total_amount:,.2f}. Above normal activity threshold.",
        })

    # Final score: alert baseline + small boost from detected patterns (never downgrade)
    risk_score = min(alert_base_score + driver_boost, 100)

    # Preserve the alert's risk level — investigation should confirm or escalate, never downgrade
    LEVEL_ORDER = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    if risk_score >= 80:
        computed_level = "CRITICAL"
    elif risk_score >= 60:
        computed_level = "HIGH"
    elif risk_score >= 40:
        computed_level = "MEDIUM"
    else:
        computed_level = "LOW"

    # Use whichever is higher: computed level or original alert level
    if LEVEL_ORDER.get(alert_base_level, 0) > LEVEL_ORDER.get(computed_level, 0):
        risk_level = alert_base_level
    else:
        risk_level = computed_level

    overall_confidence = round(
        sum(d["confidence"] for d in drivers) / max(len(drivers), 1), 2
    )

    return {
        "alert_id": alert_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "confidence": overall_confidence,
        "drivers": drivers,
        "summary": _build_summary(alert, drivers, risk_score, risk_level),
    }


def _build_summary(alert, drivers, risk_score, risk_level):
    entity_name = alert.get("entity_name", "Unknown Entity")
    n_drivers = len(drivers)
    top_driver = drivers[0]["indicator"] if drivers else "No specific risk identified"
    return (
        f"Risk assessment for {entity_name}: {risk_level} risk (score: {risk_score}/100). "
        f"{n_drivers} risk driver(s) identified. Primary concern: {top_driver}. "
        f"Recommended for {'immediate escalation' if risk_level == 'CRITICAL' else 'detailed review' if risk_level == 'HIGH' else 'standard review'}."
    )


def _empty_risk(alert_id):
    return {
        "alert_id": alert_id,
        "risk_score": 0,
        "risk_level": "LOW",
        "confidence": 0.0,
        "drivers": [],
        "summary": f"No risk data available for alert {alert_id}.",
    }
