"""
Unit tests for RecoveryManager crash recovery and interrupted task handling.
"""

import pytest
from src.agents.recovery import RecoveryManager
from src.persistence.database import DatabaseManager
from src.persistence.exceptions import RetryLimitExceededError, TaskNotRetryableError
from src.persistence.models import DBTask
from src.persistence.repositories import AuditRepository, TaskRepository


def test_recovery_manager_startup_sweep(tmp_path):
    db_mgr = DatabaseManager(db_path=tmp_path / "rec.db")
    task_repo = TaskRepository(db_manager=db_mgr)
    audit_repo = AuditRepository(db_manager=db_mgr)
    rec_mgr = RecoveryManager(task_repo=task_repo, audit_repo=audit_repo)

    # Setup tasks in various states
    task_repo.create_task(
        DBTask(
            task_id="t_running",
            user_id="u1",
            session_id="s1",
            task_type="CHAT",
            title="Running Task",
            query="Query",
            status="RUNNING",
            risk_level="LOW",
            requires_approval=False,
            approval_status="NOT_REQUIRED",
        )
    )
    task_repo.create_task(
        DBTask(
            task_id="t_waiting",
            user_id="u1",
            session_id="s1",
            task_type="CHAT",
            title="Waiting Task",
            query="Query",
            status="WAITING_FOR_APPROVAL",
            risk_level="HIGH",
            requires_approval=True,
            approval_status="PENDING",
        )
    )

    res = rec_mgr.process_startup_recovery()

    assert res["interrupted_tasks_count"] == 1
    assert res["waiting_approval_count"] == 1

    t_run = task_repo.get_task("t_running")
    assert t_run.status == "INTERRUPTED"

    t_wait = task_repo.get_task("t_waiting")
    assert t_wait.status == "WAITING_FOR_APPROVAL"


def test_recovery_manager_prepare_resume_and_retry(tmp_path):
    db_mgr = DatabaseManager(db_path=tmp_path / "rec2.db")
    task_repo = TaskRepository(db_manager=db_mgr)
    rec_mgr = RecoveryManager(task_repo=task_repo)

    # Create interrupted task without approval requirement
    task_repo.create_task(
        DBTask(
            task_id="t_interrupted",
            user_id="u1",
            session_id="s1",
            task_type="CHAT",
            title="Interrupted",
            query="Query",
            status="INTERRUPTED",
            risk_level="LOW",
            requires_approval=False,
            approval_status="NOT_REQUIRED",
        )
    )

    res_task = rec_mgr.prepare_resume("t_interrupted")
    assert res_task.status == "APPROVED"

    # Create failed task for retry test
    task_repo.create_task(
        DBTask(
            task_id="t_failed",
            user_id="u1",
            session_id="s1",
            task_type="CHAT",
            title="Failed",
            query="Query",
            status="FAILED",
            risk_level="LOW",
            requires_approval=False,
            approval_status="NOT_REQUIRED",
            retry_count=0,
            max_retries=2,
            error_code="TRANSIENT_TIMEOUT",
        )
    )

    retry_task = rec_mgr.prepare_retry("t_failed")
    assert retry_task.retry_count == 1
    assert retry_task.status == "APPROVED"

    # Policy violation non-retryable test
    task_repo.create_task(
        DBTask(
            task_id="t_policy_failed",
            user_id="u1",
            session_id="s1",
            task_type="CHAT",
            title="Policy Failed",
            query="Query",
            status="FAILED",
            risk_level="HIGH",
            requires_approval=True,
            approval_status="REJECTED",
            error_code="POLICY_VIOLATION",
        )
    )

    with pytest.raises(TaskNotRetryableError):
        rec_mgr.prepare_retry("t_policy_failed")
