"""
API Integration tests for /agent/tasks CRUD, state retrieval, execution history, and cancellation.
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


def test_create_and_get_durable_agent_task(client):
    # 1. Create durable task
    res_create = client.post(
        "/agent/tasks",
        json={"query": "Explain crude oil distillation process", "session_id": "s_123"},
    )
    assert res_create.status_code == 200
    json_data = res_create.json()
    assert json_data["success"] is True
    task_id = json_data["data"]["task_id"]
    assert task_id.startswith("task_")

    # 2. Get durable task state
    res_get = client.get(f"/agent/tasks/{task_id}")
    assert res_get.status_code == 200
    assert res_get.json()["data"]["task_id"] == task_id
    assert res_get.json()["data"]["query"] == "Explain crude oil distillation process"

    # 3. List tasks
    res_list = client.get("/agent/tasks")
    assert res_list.status_code == 200
    assert res_list.json()["data"]["total_count"] >= 1

    # 4. Cancel task
    res_cancel = client.post(f"/agent/tasks/{task_id}/cancel")
    assert res_cancel.status_code == 200
    assert res_cancel.json()["data"]["status"] == "CANCELLED"
