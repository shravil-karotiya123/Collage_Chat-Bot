"""
Unit tests for GET /router API endpoint.
"""

from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


def test_get_router_endpoint() -> None:
    response = client.get("/router")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["status_code"] == 200
    data = payload["data"]
    assert data["router_class"] == "ModelRouter"
    assert "intent_mappings" in data
    assert data["intent_mappings"]["CODING"] == "CoderManager"
    assert data["intent_mappings"]["IMAGE"] == "VisionManager"
    assert data["intent_mappings"]["GENERAL_CHAT"] == "QwenManager"
