import networkx as nx
from typing import List

class GraphBuilder:
    """Creates a transient DiGraph per request and serializes to a D3-compatible dict."""

    def build_from_transactions(self, entities: List[dict], transactions: List[dict]) -> dict:
        """
        Build a fresh graph per call (no shared state), return D3-ready {nodes, links}.
        """
        g = nx.DiGraph()

        HIGH_RISK_JURISDICTIONS = {"IR", "MM", "KP", "SY", "YE", "SO", "CD", "ML", "CF", "SS"}

        for e in entities:
            risk = 1 if e.get("jurisdiction") in HIGH_RISK_JURISDICTIONS else 0
            is_sdn = e.get("attributes", {}).get("is_sdn", False) if isinstance(e.get("attributes"), dict) else False
            g.add_node(
                e["id"],
                name=e.get("name", e["id"]),
                type=e.get("type", "individual"),
                risk_weight=risk,
                is_sdn=is_sdn,
                is_shell_suspect=e.get("is_shell_suspect", False),
            )

        for t in transactions:
            for node_id in (t["source_id"], t["target_id"]):
                if not g.has_node(node_id):
                    g.add_node(node_id, name=node_id, type="account",
                               risk_weight=0, is_sdn=False, is_shell_suspect=False)
            g.add_edge(
                t["source_id"],
                t["target_id"],
                amount=t.get("amount", 0),
                date=t.get("date", ""),
                tx_type=t.get("type", "wire"),
            )

        # Serialize manually to guarantee D3 compatibility:
        # nodes = [{id, name, type, ...attrs}], links = [{source, target, amount}]
        nodes = [{"id": n, **attrs} for n, attrs in g.nodes(data=True)]
        links = [
            {"source": u, "target": v, "amount": data.get("amount", 0), "tx_type": data.get("tx_type", "wire")}
            for u, v, data in g.edges(data=True)
        ]

        return {"nodes": nodes, "links": links}
