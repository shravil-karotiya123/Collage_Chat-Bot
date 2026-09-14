"""
Unit tests for GET /health API endpoint.
"""

from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


def test_get_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["status_code"] == 200
    assert payload["data"]["status"] == "healthy"
    assert "active_runtime" in payload["data"]
    assert "model_health" in payload["data"]
