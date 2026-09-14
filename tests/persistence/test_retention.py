"""
Unit tests for RetentionManager expired record purging.
"""

from datetime import datetime, timedelta, timezone
from src.persistence.database import DatabaseManager
from src.persistence.models import DBTask
from src.persistence.repositories import TaskRepository
from src.persistence.retention import RetentionManager


def test_retention_manager_purging(tmp_path):
    db_mgr = DatabaseManager(db_path=tmp_path / "retention.db")
    task_repo = TaskRepository(db_manager=db_mgr)

    old_date = (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
    recent_date = datetime.now(timezone.utc).isoformat()

    # 1. Create old completed task (should be purged)
    task_repo.create_task(
        DBTask(
            task_id="task_old_completed",
            user_id="user1",
            session_id="s1",
            task_type="CHAT",
            title="Old",
            query="Old query",
            status="COMPLETED",
            risk_level="LOW",
            requires_approval=False,
            approval_status="NOT_REQUIRED",
            created_at=old_date,
            updated_at=old_date,
        )
    )

    # 2. Create old RUNNING task (should NOT be purged because it's protected)
    task_repo.create_task(
        DBTask(
            task_id="task_old_running",
            user_id="user1",
            session_id="s1",
            task_type="CHAT",
            title="Old Running",
            query="Running query",
            status="RUNNING",
            risk_level="LOW",
            requires_approval=False,
            approval_status="NOT_REQUIRED",
            created_at=old_date,
            updated_at=old_date,
        )
    )

    # 3. Create recent completed task (should NOT be purged because it's recent)
    task_repo.create_task(
        DBTask(
            task_id="task_recent_completed",
            user_id="user1",
            session_id="s1",
            task_type="CHAT",
            title="Recent",
            query="Recent query",
            status="COMPLETED",
            risk_level="LOW",
            requires_approval=False,
            approval_status="NOT_REQUIRED",
            created_at=recent_date,
            updated_at=recent_date,
        )
    )

    retention_mgr = RetentionManager(db_manager=db_mgr, retention_days=30)
    res = retention_mgr.purge_expired_records()

    assert res["purged_tasks_count"] == 1
    assert task_repo.get_task("task_old_completed") is None
    assert task_repo.get_task("task_old_running") is not None
    assert task_repo.get_task("task_recent_completed") is not None
