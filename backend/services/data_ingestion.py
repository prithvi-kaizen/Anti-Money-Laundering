"""
Sentinel AML — Data Ingestion Service
Loads synthetic datasets into in-memory stores.
"""

import json
import os
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# In-memory data stores
_entities: list[dict] = []
_accounts: list[dict] = []
_transactions: list[dict] = []
_sanctions: list[dict] = []
_alerts: list[dict] = []

_loaded = False


def load_all_data():
    """Load all datasets from JSON files into memory."""
    global _entities, _accounts, _transactions, _sanctions, _alerts, _loaded

    if _loaded:
        return

    files = {
        "entities": "entities.json",
        "accounts": "accounts.json",
        "transactions": "transactions.json",
        "sanctions": "sanctions.json",
        "alerts": "alerts.json",
    }

    for key, filename in files.items():
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dataset not found: {filepath}. Run generate_dataset.py first.")
        with open(filepath, "r") as f:
            data = json.load(f)
            if key == "entities":
                _entities = data
            elif key == "accounts":
                _accounts = data
            elif key == "transactions":
                _transactions = data
            elif key == "sanctions":
                _sanctions = data
            elif key == "alerts":
                _alerts = data

    _loaded = True
    print(f"✅ Data loaded: {len(_entities)} entities, {len(_accounts)} accounts, "
          f"{len(_transactions)} transactions, {len(_sanctions)} sanctions, {len(_alerts)} alerts")


def get_entities() -> list[dict]:
    return _entities


def get_accounts() -> list[dict]:
    return _accounts


def get_transactions() -> list[dict]:
    return _transactions


def get_sanctions() -> list[dict]:
    return _sanctions


def get_alerts() -> list[dict]:
    return _alerts


def get_alert_by_id(alert_id: str) -> Optional[dict]:
    return next((a for a in _alerts if a["alert_id"] == alert_id), None)


def get_entity_by_id(entity_id: str) -> Optional[dict]:
    return next((e for e in _entities if e["entity_id"] == entity_id), None)


def get_account_by_id(account_id: str) -> Optional[dict]:
    return next((a for a in _accounts if a["account_id"] == account_id), None)


def get_transactions_for_entity(entity_id: str) -> list[dict]:
    return [t for t in _transactions
            if t["sender_entity"] == entity_id or t["receiver_entity"] == entity_id]


def get_transactions_by_ids(tx_ids: list[str]) -> list[dict]:
    id_set = set(tx_ids)
    return [t for t in _transactions if t["tx_id"] in id_set]


def get_accounts_for_entity(entity_id: str) -> list[dict]:
    return [a for a in _accounts if a["entity_id"] == entity_id]


def check_sanctions(name: str, country: str) -> list[dict]:
    """Check if a name/country appears on sanctions list."""
    matches = []
    name_lower = name.lower()
    for s in _sanctions:
        if (s["name"].lower() in name_lower or
            name_lower in s["name"].lower() or
            any(name_lower in alias.lower() or alias.lower() in name_lower for alias in s.get("aliases", []))):
            matches.append(s)
        elif s["country"] == country:
            matches.append(s)
    return matches


def update_alert_status(alert_id: str, status: str):
    """Update alert status in memory."""
    alert = get_alert_by_id(alert_id)
    if alert:
        alert["status"] = status
