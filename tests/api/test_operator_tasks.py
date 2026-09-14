"""
API Integration tests for Operator Console persistence & recovery endpoints.
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


def test_operator_persistence_and_recovery_endpoints(client):
    # 1. Recovery status
    res_rec = client.get("/operator/recovery")
    assert res_rec.status_code == 200
    assert res_rec.json()["success"] is True
    assert "recovery_enabled" in res_rec.json()["data"]

    # 2. Persistence status
    res_status = client.get("/operator/persistence/status")
    assert res_status.status_code == 200
    assert res_status.json()["success"] is True
    assert res_status.json()["data"]["provider"] == "SQLite"

    # 3. Persistence backup creation
    res_backup = client.post("/operator/persistence/backup")
    assert res_backup.status_code == 200
    assert res_backup.json()["success"] is True
    assert res_backup.json()["data"]["status"] == "SUCCESS"
