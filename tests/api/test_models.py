"""
Unit tests for GET /models API endpoint.
"""

from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


def test_get_models_endpoint() -> None:
    response = client.get("/models")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["status_code"] == 200
    data = payload["data"]
    assert "available_models" in data
    models = data["available_models"]
    assert len(models) == 3
    from config.settings import settings
    tags = [m["tag"] for m in models]
    assert settings.QWEN_MODEL in tags
    assert settings.DEFAULT_CODER_MODEL in tags
    assert settings.DEFAULT_VISION_MODEL in tags
