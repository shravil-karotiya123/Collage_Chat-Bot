"""
API Integration tests for GET /security/offline and POST /security/offline/validate.
"""

import pytest
from fastapi.testclient import TestClient

from config.settings import settings
from src.api.app import app


@pytest.fixture
def client():
    from src.security.request_security import get_security_service
    get_security_service().rate_limiter.reset()
    c = TestClient(app)
    c.headers["Authorization"] = f"Bearer {settings.AUTH_TOKEN}"
    return c


def test_offline_security_endpoints(client):
    # 1. GET /security/offline
    res = client.get("/security/offline")
    assert res.status_code == 200
    assert res.json()["success"] is True
    data = res.json()["data"]
    assert data["offline_mode"] is True
    assert data["network_policy"] == "LOCAL_ONLY"
    assert data["ollama_local"] is True

    # 2. POST /security/offline/validate
    res_val = client.post("/security/offline/validate")
    assert res_val.status_code == 200
    assert res_val.json()["success"] is True
    val_data = res_val.json()["data"]
    assert "checks" in val_data
    assert len(val_data["checks"]) >= 5
