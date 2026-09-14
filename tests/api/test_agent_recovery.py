"""
API Integration tests for /agent/tasks/{id}/resume and /agent/tasks/{id}/retry endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from config.settings import settings
from src.api.app import app
from src.persistence import DBTask, TaskRepository


@pytest.fixture
def client():
    c = TestClient(app)
    c.headers["Authorization"] = f"Bearer {settings.AUTH_TOKEN}"
    return c


def test_resume_and_retry_api_endpoints(client):
    task_repo = TaskRepository()

    # 1. Create interrupted task directly in repo
    task_repo.create_task(
        DBTask(
            task_id="task_api_interrupted",
            user_id="operator",
            session_id="s1",
            task_type="CHAT",
            title="Interrupted Task",
            query="Query text",
            status="INTERRUPTED",
            risk_level="LOW",
            requires_approval=False,
            approval_status="NOT_REQUIRED",
        )
    )

    # Resume task via API
    res_resume = client.post("/agent/tasks/task_api_interrupted/resume")
    assert res_resume.status_code == 200
    assert res_resume.json()["success"] is True

    # 2. Create failed task for retry API
    task_repo.create_task(
        DBTask(
            task_id="task_api_failed",
            user_id="operator",
            session_id="s1",
            task_type="CHAT",
            title="Failed Task",
            query="Query text",
            status="FAILED",
            risk_level="LOW",
            requires_approval=False,
            approval_status="NOT_REQUIRED",
            retry_count=0,
            max_retries=2,
            error_code="TRANSIENT_TIMEOUT",
        )
    )

    # Retry task via API
    res_retry = client.post("/agent/tasks/task_api_failed/retry")
    assert res_retry.status_code == 200
    assert res_retry.json()["success"] is True
