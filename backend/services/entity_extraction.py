"""
Sentinel AML — Entity Extraction & Knowledge Graph Service
Builds a NetworkX graph from transactions and entities.
"""

import networkx as nx
from services.data_ingestion import (
    get_entity_by_id, get_accounts_for_entity,
    get_transactions_for_entity, get_transactions_by_ids,
    get_alert_by_id, check_sanctions
)


def build_entity_graph(alert_id: str) -> dict:
    """
    Build an entity relationship graph for a given alert.
    Returns nodes and edges suitable for frontend visualization.
    """
    alert = get_alert_by_id(alert_id)
    if not alert:
        return {"nodes": [], "edges": [], "alert_id": alert_id}

    G = nx.DiGraph()
    seen_entities = set()
    seen_accounts = set()

    # Start from the alert's primary entity
    primary_entity_id = alert["entity_id"]
    related_tx_ids = alert.get("related_transactions", [])
    transactions = get_transactions_by_ids(related_tx_ids)

    # Also get all transactions for primary entity
    entity_txs = get_transactions_for_entity(primary_entity_id)
    all_txs = {t["tx_id"]: t for t in transactions + entity_txs}

    for tx in all_txs.values():
        # Add sender entity
        sender_eid = tx["sender_entity"]
        if sender_eid not in seen_entities:
            entity = get_entity_by_id(sender_eid)
            sanctions = check_sanctions(tx["sender_name"], tx.get("sender_country", ""))
            G.add_node(sender_eid, **{
                "label": tx["sender_name"],
                "type": "entity",
                "risk": bool(entity and entity.get("risk_flag")) or bool(sanctions),
                "country": tx.get("sender_country", ""),
                "entity_type": entity.get("type", "UNKNOWN") if entity else "UNKNOWN",
                "is_primary": sender_eid == primary_entity_id,
                "sanctions_match": bool(sanctions),
            })
            seen_entities.add(sender_eid)

        # Add receiver entity
        receiver_eid = tx["receiver_entity"]
        if receiver_eid not in seen_entities:
            entity = get_entity_by_id(receiver_eid)
            sanctions = check_sanctions(tx["receiver_name"], tx.get("receiver_country", ""))
            G.add_node(receiver_eid, **{
                "label": tx["receiver_name"],
                "type": "entity",
                "risk": bool(entity and entity.get("risk_flag")) or bool(sanctions),
                "country": tx.get("receiver_country", ""),
                "entity_type": entity.get("type", "UNKNOWN") if entity else "UNKNOWN",
                "is_primary": receiver_eid == primary_entity_id,
                "sanctions_match": bool(sanctions),
            })
            seen_entities.add(receiver_eid)

        # Add sender account
        s_acc = tx["sender_account"]
        if s_acc not in seen_accounts:
            G.add_node(s_acc, **{
                "label": s_acc,
                "type": "account",
                "risk": False,
                "country": tx.get("sender_country", ""),
            })
            seen_accounts.add(s_acc)
            G.add_edge(sender_eid, s_acc, label="owns", amount=None, tx_id=None)

        # Add receiver account
        r_acc = tx["receiver_account"]
        if r_acc not in seen_accounts:
            G.add_node(r_acc, **{
                "label": r_acc,
                "type": "account",
                "risk": False,
                "country": tx.get("receiver_country", ""),
            })
            seen_accounts.add(r_acc)
            G.add_edge(receiver_eid, r_acc, label="owns", amount=None, tx_id=None)

        # Add transaction edge
        G.add_edge(s_acc, r_acc, **{
            "label": f"${tx['amount']:,.2f}",
            "amount": tx["amount"],
            "tx_id": tx["tx_id"],
            "suspicious": tx.get("suspicious_pattern") is not None,
        })

    # Convert to serializable format
    nodes = []
    for node_id, data in G.nodes(data=True):
        nodes.append({
            "id": node_id,
            "label": data.get("label", node_id),
            "type": data.get("type", "unknown"),
            "risk": data.get("risk", False),
            "country": data.get("country", ""),
            "metadata": {k: v for k, v in data.items()
                         if k not in ("label", "type", "risk", "country")},
        })

    edges = []
    for src, tgt, data in G.edges(data=True):
        edges.append({
            "source": src,
            "target": tgt,
            "label": data.get("label", ""),
            "amount": data.get("amount"),
            "tx_id": data.get("tx_id"),
        })

    return {"nodes": nodes, "edges": edges, "alert_id": alert_id}
