"""
API Endpoint Integration Tests for Phase 11 (/ready, /live, /metrics, /security, /operator, /auth).
"""

import pytest
from fastapi.testclient import TestClient

from config.settings import settings
from src.api.app import app


@pytest.fixture
def client():
    c = TestClient(app)
    c.headers["Authorization"] = f"Bearer {settings.AUTH_TOKEN}"
    return c


def test_liveness_and_readiness_endpoints(client):
    # Liveness probe
    res_live = client.get("/live")
    assert res_live.status_code == 200
    assert res_live.json()["data"]["status"] == "alive"

    # Readiness probe
    res_ready = client.get("/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["success"] is True
    assert "ready" in res_ready.json()["data"]


def test_metrics_endpoint(client):
    res = client.get("/metrics")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert "metrics" in json_data["data"]


def test_security_status_and_policy_endpoints(client):
    # Security Status
    res_stat = client.get("/security/status")
    assert res_stat.status_code == 200
    assert res_stat.json()["data"]["status"] == "healthy"

    # Security Policy
    res_pol = client.get("/security/policy")
    assert res_pol.status_code == 200
    assert len(res_pol.json()["data"]["blocked_tools"]) >= 1


def test_operator_dashboard_endpoint(client):
    res = client.get("/operator/dashboard")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "MRPL AI WORKBENCH" in res.text
