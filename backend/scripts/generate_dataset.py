import json
import os
from datetime import datetime, timedelta

def generate_synthetic_data():
    base_date = datetime.now()
    
    entities = [
        # Scenario A
        {"id": "e_001", "name": "Ahmad Khalil", "type": "person", "jurisdiction": "US", "risk_score": 0.4},
        {"id": "e_002", "name": "Khalil Trading LLC", "type": "company", "jurisdiction": "US", "risk_score": 0.5},
        
        # Scenario B
        {"id": "e_003", "name": "Nexus Capital Ltd", "type": "company", "jurisdiction": "KY", "risk_score": 0.9, "is_shell_suspect": True},
        {"id": "e_004", "name": "Correspondent Bank Iran", "type": "company", "jurisdiction": "IR", "risk_score": 1.0},
        {"id": "e_005", "name": "UAE Shell Provider", "type": "company", "jurisdiction": "AE", "risk_score": 0.8},
        {"id": "e_006", "name": "Singapore Fintech", "type": "company", "jurisdiction": "SG", "risk_score": 0.5},
        {"id": "e_007", "name": "US Bank Account", "type": "company", "jurisdiction": "US", "risk_score": 0.2},
        
        # Scenario C
        {"id": "e_008", "name": "Sunrise Properties GmbH", "type": "company", "jurisdiction": "DE", "risk_score": 0.6},
        {"id": "e_009", "name": "Intermediary LLC 1", "type": "company", "jurisdiction": "CY", "risk_score": 0.8, "is_shell_suspect": True},
        {"id": "e_010", "name": "Intermediary LLC 2", "type": "company", "jurisdiction": "CH", "risk_score": 0.7, "is_shell_suspect": True},
        {"id": "e_011", "name": "Intermediary LLC 3", "type": "company", "jurisdiction": "MT", "risk_score": 0.8, "is_shell_suspect": True},
        {"id": "e_012", "name": "Intermediary LLC 4", "type": "company", "jurisdiction": "LI", "risk_score": 0.9, "is_shell_suspect": True},
        
        # Scenario D
        {"id": "e_013", "name": "Alpha Holdings", "type": "company", "jurisdiction": "US", "risk_score": 0.7, "is_shell_suspect": True},
        {"id": "e_014", "name": "Beta Ventures", "type": "company", "jurisdiction": "US", "risk_score": 0.7, "is_shell_suspect": True},
        {"id": "e_015", "name": "Gamma Associates", "type": "company", "jurisdiction": "US", "risk_score": 0.7, "is_shell_suspect": True},
        
        # Scenario E
        {"id": "e_016", "name": "Meridian Trade Co", "type": "company", "jurisdiction": "GB", "risk_score": 0.5},
        {"id": "e_017", "name": "Supplier A", "type": "company", "jurisdiction": "CN", "risk_score": 0.6},
        {"id": "e_018", "name": "Manufacturer B", "type": "company", "jurisdiction": "RU", "risk_score": 0.9},
        {"id": "e_019", "name": "Sanctioned Entity XYZ", "type": "company", "jurisdiction": "RU", "risk_score": 1.0, "attributes": {"is_sdn": True}},
    ]
    
    transactions = []
    
    # Scenario A: Structuring (6 deposits)
    amounts_A = [9200, 9450, 9100, 9800, 9350, 9600]
    for i, amt in enumerate(amounts_A):
        transactions.append({
            "id": f"t_A_{i}", "source_id": "e_001", "target_id": "e_002",
            "amount": amt, "currency": "USD", "type": "cash",
            "date": (base_date - timedelta(days=12-i*2)).isoformat()
        })
        
    # Scenario B: Jurisdiction Layering ($2.3M wire over 6 days)
    path_B = ["e_003", "e_004", "e_005", "e_006", "e_007"]
    for i in range(len(path_B)-1):
        transactions.append({
            "id": f"t_B_{i}", "source_id": path_B[i], "target_id": path_B[i+1],
            "amount": 2300000.0, "currency": "USD", "type": "wire",
            "date": (base_date - timedelta(days=6-i)).isoformat()
        })
        
    # Scenario C: Round-Trip (72 hours)
    path_C = ["e_008", "e_009", "e_010", "e_011", "e_012", "e_008"]
    for i in range(len(path_C)-1):
        transactions.append({
            "id": f"t_C_{i}", "source_id": path_C[i], "target_id": path_C[i+1],
            "amount": 800000.0, "currency": "USD", "type": "wire",
            "date": (base_date - timedelta(hours=72 - i*12)).isoformat()
        })
        
    # Scenario D: Shell Network (circular, ~450k)
    path_D = ["e_013", "e_014", "e_015", "e_013"]
    for i in range(len(path_D)-1):
        transactions.append({
            "id": f"t_D_{i}", "source_id": path_D[i], "target_id": path_D[i+1],
            "amount": 150000.0, "currency": "USD", "type": "wire",
            "date": (base_date - timedelta(days=5-i)).isoformat()
        })
        
    # Scenario E: Sanctions Proxy (1.1M)
    path_E = ["e_016", "e_017", "e_018", "e_019"]
    for i in range(len(path_E)-1):
        transactions.append({
            "id": f"t_E_{i}", "source_id": path_E[i], "target_id": path_E[i+1],
            "amount": 1100000.0, "currency": "USD", "type": "wire",
            "date": (base_date - timedelta(days=3-i)).isoformat()
        })
        
    alerts = [
        {"id": "alert_001", "entity_id": "e_001", "rule_triggered": "STRUCTURING", "severity": "CRITICAL", "timestamp": base_date.isoformat(), "status": "OPEN", "title": "Structuring Detection"},
        {"id": "alert_002", "entity_id": "e_003", "rule_triggered": "HIGH_RISK_JURISDICTION", "severity": "CRITICAL", "timestamp": base_date.isoformat(), "status": "OPEN", "title": "Jurisdiction Layering"},
        {"id": "alert_003", "entity_id": "e_008", "rule_triggered": "ROUND_TRIP", "severity": "HIGH", "timestamp": base_date.isoformat(), "status": "OPEN", "title": "Round-Trip Integration"},
        {"id": "alert_004", "entity_id": "e_013", "rule_triggered": "SHELL_COMPANY", "severity": "HIGH", "timestamp": base_date.isoformat(), "status": "OPEN", "title": "Shell Company Network"},
        {"id": "alert_005", "entity_id": "e_016", "rule_triggered": "SANCTIONS_PROXIMITY", "severity": "CRITICAL", "timestamp": base_date.isoformat(), "status": "OPEN", "title": "Sanctions Proximity (2-hop)"},
    ]
    
    os.makedirs(os.path.dirname(os.path.abspath(__file__)) + "/../data", exist_ok=True)
    with open(os.path.dirname(os.path.abspath(__file__)) + "/../data/dataset.json", "w") as f:
        json.dump({
            "entities": entities,
            "transactions": transactions,
            "alerts": alerts
        }, f, indent=2)

if __name__ == "__main__":
    generate_synthetic_data()
    print("Synthetic dataset generated successfully.")
