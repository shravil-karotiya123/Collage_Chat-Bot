"""
Unit tests for TaskRepository CRUD, filtering, pagination, and secret redaction.
"""

from src.persistence.database import DatabaseManager
from src.persistence.models import DBPlan, DBTask
from src.persistence.repositories import TaskRepository, redact_sensitive_data, truncate_excerpt


def test_redact_sensitive_data():
    raw = {
        "user_query": "Explain oil pressure",
        "password": "supersecretpassword",
        "access_token": "mrpl_bearer_token",
        "reasoning": "Internal chain of thought reasoning",
        "normal_meta": {"ip": "127.0.0.1"},
    }

    cleaned = redact_sensitive_data(raw)
    assert cleaned["user_query"] == "Explain oil pressure"
    assert cleaned["password"] == "[REDACTED_SECRET]"
    assert cleaned["access_token"] == "[REDACTED_SECRET]"
    assert cleaned["reasoning"] == "[REDACTED_SECRET]"
    assert cleaned["normal_meta"]["ip"] == "127.0.0.1"


def test_truncate_excerpt():
    long_text = "A" * 5000
    truncated = truncate_excerpt(long_text, max_len=100)
    assert len(truncated) < 200
    assert "... [TRUNCATED" in truncated


def test_task_repository_crud(tmp_path):
    db_mgr = DatabaseManager(db_path=tmp_path / "repo.db")
    repo = TaskRepository(db_manager=db_mgr)

    task = DBTask(
        task_id="task_test_100",
        user_id="user_admin",
        session_id="session_1",
        task_type="CODING",
        title="Refinery Code",
        query="Write Python script",
        status="CREATED",
        risk_level="LOW",
        requires_approval=False,
        approval_status="NOT_REQUIRED",
        metadata={"password": "secret_data"},
    )

    # 1. Create
    repo.create_task(task)

    # 2. Get
    fetched = repo.get_task("task_test_100")
    assert fetched is not None
    assert fetched.task_id == "task_test_100"
    assert fetched.user_id == "user_admin"
    assert fetched.metadata["password"] == "[REDACTED_SECRET]"

    # 3. Update
    fetched.status = "APPROVED"
    fetched.approval_status = "APPROVED"
    repo.update_task(fetched)

    updated = repo.get_task("task_test_100")
    assert updated.status == "APPROVED"

    # 4. List
    tasks, count = repo.list_tasks(user_id="user_admin")
    assert count == 1
    assert tasks[0].task_id == "task_test_100"
