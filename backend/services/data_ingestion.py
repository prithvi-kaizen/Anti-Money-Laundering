import json
import os
from models import Entity, Transaction, Alert

DATA_FILE = os.path.dirname(os.path.abspath(__file__)) + "/../data/dataset.json"

class DataIngestion:
    def __init__(self):
        self.entities = []
        self.transactions = []
        self.alerts = []
        self._load_data()

    def _load_data(self):
        if not os.path.exists(DATA_FILE):
            return
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            self.entities = [Entity(**e) for e in data.get("entities", [])]
            self.transactions = [Transaction(**t) for t in data.get("transactions", [])]
            self.alerts = [Alert(**a) for a in data.get("alerts", [])]

    def get_all_alerts(self):
        return self.alerts

    def get_alert(self, alert_id: str):
        return next((a for a in self.alerts if a.id == alert_id), None)

    def get_entity(self, entity_id: str):
        return next((e for e in self.entities if e.id == entity_id), None)

    def get_related_transactions(self, entity_id: str):
        # Very simple graph walk: get all transactions directly involving this entity, or up to 2 hops.
        # For simplicity in demo, just return transactions that form the path for this entity's scenario.
        # e.g., for e_001, t_A_*
        scenario_map = {
            "e_001": "t_A",
            "e_003": "t_B",
            "e_008": "t_C",
            "e_013": "t_D",
            "e_016": "t_E"
        }
        prefix = scenario_map.get(entity_id)
        if prefix:
            return [t for t in self.transactions if t.id.startswith(prefix)]
        return []

    def get_all_scenario_entities(self, entity_id: str):
        # Grab all entities in the same scenario
        txs = self.get_related_transactions(entity_id)
        e_ids = set()
        for t in txs:
            e_ids.add(t.source_id)
            e_ids.add(t.target_id)
        e_ids.add(entity_id)
        return [self.get_entity(eid) for eid in e_ids if self.get_entity(eid)]
