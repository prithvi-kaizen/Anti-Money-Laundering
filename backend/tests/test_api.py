"""
Sentinel AML — API Tests
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app
from services.data_ingestion import load_all_data, get_transactions
from services.rag_pipeline import build_evidence_index

# Load data before tests (startup event doesn't fire with TestClient)
load_all_data()
build_evidence_index(get_transactions())

client = TestClient(app)


class TestHealthAndRoot:
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Sentinel AML Investigator"
        assert data["status"] == "operational"

    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestAlerts:
    def test_list_alerts(self):
        response = client.get("/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "total" in data
        assert data["total"] > 0
        # Check first alert structure
        alert = data["alerts"][0]
        assert "alert_id" in alert
        assert "entity_name" in alert
        assert "risk_score" in alert
        assert "risk_level" in alert

    def test_list_alerts_filter_risk(self):
        response = client.get("/alerts?risk_level=CRITICAL")
        assert response.status_code == 200
        data = response.json()
        for alert in data["alerts"]:
            assert alert["risk_level"] == "CRITICAL"

    def test_get_alert_detail(self):
        # Get first alert ID
        alerts_response = client.get("/alerts")
        alert_id = alerts_response.json()["alerts"][0]["alert_id"]

        response = client.get(f"/alerts/{alert_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["alert_id"] == alert_id
        assert "transactions" in data

    def test_get_alert_not_found(self):
        response = client.get("/alerts/NONEXISTENT")
        assert response.status_code == 404


class TestGraph:
    def test_get_graph(self):
        alerts_response = client.get("/alerts")
        alert_id = alerts_response.json()["alerts"][0]["alert_id"]

        response = client.get(f"/alerts/{alert_id}/graph")
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert data["alert_id"] == alert_id
        assert len(data["nodes"]) > 0

        # Check node structure
        node = data["nodes"][0]
        assert "id" in node
        assert "label" in node
        assert "type" in node

    def test_graph_not_found(self):
        response = client.get("/alerts/NONEXISTENT/graph")
        assert response.status_code == 404


class TestSAR:
    def test_generate_sar(self):
        alerts_response = client.get("/alerts")
        alert_id = alerts_response.json()["alerts"][0]["alert_id"]

        response = client.post(f"/alerts/{alert_id}/sar")
        assert response.status_code == 200
        data = response.json()

        # Validate SAR structure
        assert "sar_id" in data
        assert "case_overview" in data
        assert "timeline" in data
        assert "risk_indicators" in data
        assert "linked_entities" in data
        assert "evidence_citations" in data
        assert "recommended_action" in data
        assert "overall_risk_score" in data
        assert "overall_confidence" in data

        # Verify evidence citations have required fields
        for citation in data["evidence_citations"]:
            assert "evidence_id" in citation
            assert "type" in citation
            assert "description" in citation
            assert "source_ids" in citation
            assert "confidence" in citation
            assert 0 <= citation["confidence"] <= 1

    def test_sar_not_found(self):
        response = client.post("/alerts/NONEXISTENT/sar")
        assert response.status_code == 404


class TestInvestigation:
    def test_full_investigation(self):
        alerts_response = client.get("/alerts")
        alert_id = alerts_response.json()["alerts"][0]["alert_id"]

        response = client.post(f"/alerts/{alert_id}/investigate")
        assert response.status_code == 200
        data = response.json()

        # Verify all components present
        assert "sar" in data
        assert "risk_explanation" in data
        assert "graph" in data
        assert "audit_trail" in data

        # Verify SAR
        assert data["sar"]["sar_id"].startswith("SAR-")
        assert len(data["sar"]["evidence_citations"]) > 0

        # Verify risk explanation
        assert "risk_score" in data["risk_explanation"]
        assert "drivers" in data["risk_explanation"]

        # Verify graph
        assert len(data["graph"]["nodes"]) > 0
        assert len(data["graph"]["edges"]) > 0

        # Verify audit trail
        assert len(data["audit_trail"]["entries"]) > 0


class TestAudit:
    def test_audit_after_investigation(self):
        alerts_response = client.get("/alerts")
        alert_id = alerts_response.json()["alerts"][0]["alert_id"]

        # First investigate
        client.post(f"/alerts/{alert_id}/investigate")

        # Then check audit
        response = client.get(f"/alerts/{alert_id}/audit")
        assert response.status_code == 200
        data = response.json()
        assert data["alert_id"] == alert_id
        assert len(data["entries"]) > 0

        # Check audit entry structure
        entry = data["entries"][0]
        assert "entry_id" in entry
        assert "timestamp" in entry
        assert "action" in entry
        assert "module" in entry


class TestTiming:
    def test_timing_comparison(self):
        response = client.get("/timing")
        assert response.status_code == 200
        data = response.json()

        assert "manual_avg_minutes" in data
        assert "sentinel_avg_minutes" in data
        assert "reduction_percent" in data
        assert data["reduction_percent"] >= 30  # Must show 30%+ reduction
        assert data["sentinel_avg_minutes"] < data["manual_avg_minutes"]
