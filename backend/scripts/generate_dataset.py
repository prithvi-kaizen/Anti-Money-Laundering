"""
Sentinel AML — Synthetic Dataset Generator
Generates AMLSim-style transactions, accounts, entities, and sanctions list.
"""

import json
import random
import os
from datetime import datetime, timedelta

random.seed(42)

# --- Configuration ---
NUM_ACCOUNTS = 100
NUM_ENTITIES = 50
NUM_TRANSACTIONS = 500
NUM_SANCTIONS = 10
NUM_ALERTS = 15

COUNTRIES = ["US", "UK", "DE", "CH", "SG", "HK", "AE", "KY", "PA", "BS", "RU", "NG", "IR", "CN", "IN"]
HIGH_RISK_COUNTRIES = ["KY", "PA", "BS", "RU", "NG", "IR"]
CITIES = {
    "US": ["New York", "Miami", "Los Angeles", "Chicago"],
    "UK": ["London", "Manchester", "Birmingham"],
    "DE": ["Frankfurt", "Berlin", "Munich"],
    "CH": ["Zurich", "Geneva"],
    "SG": ["Singapore"],
    "HK": ["Hong Kong"],
    "AE": ["Dubai", "Abu Dhabi"],
    "KY": ["George Town"],
    "PA": ["Panama City"],
    "BS": ["Nassau"],
    "RU": ["Moscow", "St Petersburg"],
    "NG": ["Lagos", "Abuja"],
    "IR": ["Tehran"],
    "CN": ["Shanghai", "Beijing", "Shenzhen"],
    "IN": ["Mumbai", "Delhi", "Bangalore"],
}

FIRST_NAMES = ["James", "Maria", "Ahmed", "Wei", "Olga", "Carlos", "Priya", "Hans", "Fatima", "John",
               "Sarah", "Li", "Ivan", "Ana", "Mohammed", "Yuki", "Dmitri", "Elena", "Robert", "Chen",
               "Nikolai", "Svetlana", "Miguel", "Aisha", "Kenji", "Petra", "Omar", "Lucia", "Viktor", "Mei"]
LAST_NAMES = ["Smith", "Wang", "Mueller", "Petrov", "Al-Rashid", "Garcia", "Sharma", "Tanaka", "Johnson",
              "Kim", "Ivanov", "Santos", "Chen", "Brown", "Okafor", "Sato", "Kozlov", "Fischer", "Ali", "Park"]

ENTITY_TYPES = ["INDIVIDUAL", "CORPORATION", "SHELL_COMPANY", "TRUST", "NGO"]
ACCOUNT_TYPES = ["CHECKING", "SAVINGS", "BUSINESS", "OFFSHORE", "INVESTMENT"]

TX_TYPES = ["WIRE", "ACH", "INTERNAL_TRANSFER", "CASH_DEPOSIT", "CASH_WITHDRAWAL", "CHECK", "CRYPTO"]

SUSPICIOUS_PATTERNS = ["structuring", "rapid_movement", "round_trip", "sanctions_proximity", "layering"]


def generate_entities():
    entities = []
    for i in range(NUM_ENTITIES):
        country = random.choice(COUNTRIES)
        etype = random.choice(ENTITY_TYPES)
        if etype == "INDIVIDUAL":
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        elif etype == "CORPORATION":
            name = f"{random.choice(LAST_NAMES)} {random.choice(['Holdings', 'International', 'Trading', 'Capital', 'Enterprises'])} {'Ltd' if country in ['UK', 'HK', 'SG'] else 'Inc' if country == 'US' else 'GmbH' if country == 'DE' else 'SA'}"
        elif etype == "SHELL_COMPANY":
            name = f"{random.choice(['Atlas', 'Meridian', 'Apex', 'Zenith', 'Horizon'])} {random.choice(['Partners', 'Ventures', 'Holdings', 'Capital'])} {random.choice(['LLC', 'Ltd', 'SA', 'BV'])}"
        elif etype == "TRUST":
            name = f"The {random.choice(LAST_NAMES)} Family Trust"
        else:
            name = f"{random.choice(LAST_NAMES)} {random.choice(['Foundation', 'Aid Society', 'Relief Fund'])}"

        city = random.choice(CITIES.get(country, ["Unknown"]))
        entities.append({
            "entity_id": f"ENT-{i+1:04d}",
            "name": name,
            "type": etype,
            "country": country,
            "city": city,
            "risk_flag": country in HIGH_RISK_COUNTRIES or etype == "SHELL_COMPANY",
            "pep": random.random() < 0.08,
            "registered_date": (datetime(2015, 1, 1) + timedelta(days=random.randint(0, 3000))).strftime("%Y-%m-%d"),
        })
    return entities


def generate_accounts(entities):
    accounts = []
    for i in range(NUM_ACCOUNTS):
        entity = random.choice(entities)
        accounts.append({
            "account_id": f"ACC-{i+1:06d}",
            "entity_id": entity["entity_id"],
            "entity_name": entity["name"],
            "account_type": random.choice(ACCOUNT_TYPES),
            "currency": random.choice(["USD", "EUR", "GBP", "CHF", "SGD", "HKD"]),
            "country": entity["country"],
            "opened_date": (datetime(2018, 1, 1) + timedelta(days=random.randint(0, 2000))).strftime("%Y-%m-%d"),
            "status": random.choice(["ACTIVE", "ACTIVE", "ACTIVE", "DORMANT", "FROZEN"]),
        })
    return accounts


def generate_transactions(accounts):
    transactions = []
    base_date = datetime(2024, 1, 1)

    for i in range(NUM_TRANSACTIONS):
        sender = random.choice(accounts)
        receiver = random.choice([a for a in accounts if a["account_id"] != sender["account_id"]])
        tx_date = base_date + timedelta(days=random.randint(0, 365), hours=random.randint(0, 23), minutes=random.randint(0, 59))

        pattern = None
        amount = round(random.uniform(100, 500000), 2)

        # Inject suspicious patterns
        if random.random() < 0.15:
            pattern = random.choice(SUSPICIOUS_PATTERNS)
            if pattern == "structuring":
                amount = round(random.uniform(8000, 9999), 2)  # Just under $10k
            elif pattern == "rapid_movement":
                amount = round(random.uniform(50000, 200000), 2)
            elif pattern == "round_trip":
                amount = round(random.uniform(100000, 500000), 2)
            elif pattern == "layering":
                amount = round(random.uniform(25000, 150000), 2)

        transactions.append({
            "tx_id": f"TX-{i+1:06d}",
            "date": tx_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "sender_account": sender["account_id"],
            "sender_entity": sender["entity_id"],
            "sender_name": sender["entity_name"],
            "receiver_account": receiver["account_id"],
            "receiver_entity": receiver["entity_id"],
            "receiver_name": receiver["entity_name"],
            "amount": amount,
            "currency": sender["currency"],
            "tx_type": random.choice(TX_TYPES),
            "sender_country": sender["country"],
            "receiver_country": receiver["country"],
            "suspicious_pattern": pattern,
            "description": _generate_description(pattern, sender, receiver, amount),
        })

    transactions.sort(key=lambda x: x["date"])
    return transactions


def _generate_description(pattern, sender, receiver, amount):
    if pattern == "structuring":
        return f"Cash deposit of ${amount:,.2f} — just below reporting threshold. Multiple similar deposits detected from {sender['entity_name']}."
    elif pattern == "rapid_movement":
        return f"Rapid wire transfer of ${amount:,.2f} from {sender['entity_name']} ({sender['country']}) to {receiver['entity_name']} ({receiver['country']}). Funds moved within 24 hours of receipt."
    elif pattern == "round_trip":
        return f"Funds of ${amount:,.2f} routed from {sender['entity_name']} through intermediary and returned to origin. Possible round-trip transaction."
    elif pattern == "sanctions_proximity":
        return f"Transfer of ${amount:,.2f} involving entity with proximity to sanctioned jurisdiction. Sender: {sender['entity_name']}, Receiver: {receiver['entity_name']}."
    elif pattern == "layering":
        return f"Complex layering pattern detected: ${amount:,.2f} moved through multiple accounts. {sender['entity_name']} → {receiver['entity_name']}."
    else:
        descs = [
            f"Wire transfer of ${amount:,.2f} from {sender['entity_name']} to {receiver['entity_name']}.",
            f"Payment of ${amount:,.2f} — {sender['entity_name']} to {receiver['entity_name']}. Business services.",
            f"International transfer ${amount:,.2f}. {sender['country']} → {receiver['country']}.",
            f"Funds transfer of ${amount:,.2f} between accounts. Reference: INV-{random.randint(100000,999999)}.",
        ]
        return random.choice(descs)


def generate_sanctions():
    sanctions = []
    for i in range(NUM_SANCTIONS):
        country = random.choice(HIGH_RISK_COUNTRIES)
        sanctions.append({
            "sanction_id": f"SDN-{i+1:04d}",
            "name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            "aliases": [f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}" for _ in range(random.randint(1, 3))],
            "country": country,
            "type": random.choice(["INDIVIDUAL", "ENTITY"]),
            "program": random.choice(["OFAC-SDN", "EU-SANCTIONS", "UN-CONSOLIDATED", "UK-SANCTIONS"]),
            "listed_date": (datetime(2015, 1, 1) + timedelta(days=random.randint(0, 3500))).strftime("%Y-%m-%d"),
            "reason": random.choice([
                "Money laundering",
                "Terrorism financing",
                "Narcotics trafficking",
                "WMD proliferation",
                "Corruption",
                "Human rights abuse",
            ]),
        })
    return sanctions


def generate_alerts(transactions, entities, sanctions):
    alerts = []
    suspicious_txs = [t for t in transactions if t["suspicious_pattern"]]
    random.shuffle(suspicious_txs)

    for i in range(NUM_ALERTS):
        # Pick a cluster of suspicious transactions for this alert
        anchor_tx = suspicious_txs[i % len(suspicious_txs)]
        entity_id = anchor_tx["sender_entity"]
        entity = next((e for e in entities if e["entity_id"] == entity_id), None)

        # Gather related transactions
        related_txs = [t["tx_id"] for t in transactions
                       if t["sender_entity"] == entity_id or t["receiver_entity"] == entity_id][:10]

        # Check sanctions proximity
        sanctions_match = any(
            s["country"] == (entity["country"] if entity else "")
            for s in sanctions
        )

        risk_score = random.randint(40, 99)
        if sanctions_match:
            risk_score = max(risk_score, 75)
        if entity and entity["risk_flag"]:
            risk_score = max(risk_score, 65)

        if risk_score >= 80:
            risk_level = "CRITICAL"
        elif risk_score >= 60:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        alerts.append({
            "alert_id": f"ALT-{i+1:04d}",
            "entity_id": entity_id,
            "entity_name": entity["name"] if entity else "Unknown",
            "entity_type": entity["type"] if entity else "UNKNOWN",
            "country": entity["country"] if entity else "XX",
            "risk_score": risk_score,
            "risk_level": risk_level,
            "trigger_pattern": anchor_tx["suspicious_pattern"],
            "trigger_tx": anchor_tx["tx_id"],
            "related_transactions": related_txs,
            "sanctions_match": sanctions_match,
            "created_date": anchor_tx["date"],
            "status": random.choice(["NEW", "NEW", "NEW", "UNDER_REVIEW", "ESCALATED"]),
            "assigned_to": None,
            "summary": f"Suspicious activity detected for {entity['name'] if entity else 'Unknown'} — "
                       f"{anchor_tx['suspicious_pattern'].replace('_', ' ')} pattern identified. "
                       f"Risk score: {risk_score}/100.",
        })

    alerts.sort(key=lambda x: -x["risk_score"])
    return alerts


def main():
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(output_dir, exist_ok=True)

    print("🔄 Generating synthetic AML dataset...")

    entities = generate_entities()
    print(f"  ✅ {len(entities)} entities generated")

    accounts = generate_accounts(entities)
    print(f"  ✅ {len(accounts)} accounts generated")

    transactions = generate_transactions(accounts)
    print(f"  ✅ {len(transactions)} transactions generated")

    sanctions = generate_sanctions()
    print(f"  ✅ {len(sanctions)} sanctions entries generated")

    alerts = generate_alerts(transactions, entities, sanctions)
    print(f"  ✅ {len(alerts)} alerts generated")

    datasets = {
        "entities.json": entities,
        "accounts.json": accounts,
        "transactions.json": transactions,
        "sanctions.json": sanctions,
        "alerts.json": alerts,
    }

    for filename, data in datasets.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  💾 Saved {filepath}")

    # Print stats
    suspicious_count = sum(1 for t in transactions if t["suspicious_pattern"])
    print(f"\n📊 Dataset Summary:")
    print(f"   Entities: {len(entities)}")
    print(f"   Accounts: {len(accounts)}")
    print(f"   Transactions: {len(transactions)} ({suspicious_count} suspicious)")
    print(f"   Sanctions: {len(sanctions)}")
    print(f"   Alerts: {len(alerts)}")
    print(f"   High risk alerts: {sum(1 for a in alerts if a['risk_level'] in ['CRITICAL', 'HIGH'])}")
    print("✅ Dataset generation complete!")


if __name__ == "__main__":
    main()
