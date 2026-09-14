"""
API Integration tests for /agent/tasks/{id}/audit and /agent/tasks/{id}/timeline.
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


def test_agent_task_audit_and_timeline_endpoints(client):
    # 1. Create task
    res_create = client.post(
        "/agent/tasks",
        json={"query": "Calculate refinery efficiency factor"},
    )
    task_id = res_create.json()["data"]["task_id"]

    # 2. Get Audit Log
    res_audit = client.get(f"/agent/tasks/{task_id}/audit")
    assert res_audit.status_code == 200
    assert res_audit.json()["success"] is True
    assert "events" in res_audit.json()["data"]

    # 3. Get Timeline
    res_timeline = client.get(f"/agent/tasks/{task_id}/timeline")
    assert res_timeline.status_code == 200
    assert res_timeline.json()["success"] is True
    assert "timeline" in res_timeline.json()["data"]
