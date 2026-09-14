"""
Crash Recovery and Task Resilience Manager for Agentic Workflows.
Detects interrupted tasks upon application startup, preserves approval states,
and manages controlled resume and retry flows.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional

from config.settings import settings
from src.agents.agent_types import AgentStatus, ApprovalStatus
from src.agents.audit import AgentAuditLogger
from src.agents.state_machine import TaskStateMachine
from src.persistence.database import DatabaseManager, get_db_manager
from src.persistence.exceptions import (
    RecoveryFailedError,
    RetryLimitExceededError,
    TaskNotFoundError,
    TaskNotResumableError,
    TaskNotRetryableError,
)
from src.persistence.models import DBAuditEvent, DBTask
from src.persistence.repositories import AuditRepository, TaskRepository

logger = logging.getLogger("MRPL.Agents.Recovery")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RecoveryManager:
    """
    Manages application startup crash recovery, interrupted task state detection,
    controlled task resume, and bounded retries.
    """

    def __init__(
        self,
        task_repo: Optional[TaskRepository] = None,
        audit_repo: Optional[AuditRepository] = None,
        audit_logger: Optional[AgentAuditLogger] = None,
    ) -> None:
        self.task_repo = task_repo or TaskRepository()
        self.audit_repo = audit_repo or AuditRepository()
        self.audit_logger = audit_logger or AgentAuditLogger()

    def process_startup_recovery(self) -> Dict[str, Any]:
        """
        Execute startup recovery sweep across all persisted tasks.
        """
        logger.info("Executing startup task recovery check...")
        if not settings.AGENT_RECOVERY_ENABLED:
            logger.info("Agent recovery is disabled in settings.")
            return {"status": "DISABLED", "interrupted_tasks_count": 0}

        try:
            # 1. Fetch running tasks requiring state transition to INTERRUPTED
            running_tasks, _ = self.task_repo.list_tasks(status="RUNNING", limit=settings.TASK_LIST_MAX_LIMIT)
            executing_tasks, _ = self.task_repo.list_tasks(status="EXECUTING", limit=settings.TASK_LIST_MAX_LIMIT)
            active_tasks = running_tasks + executing_tasks

            interrupted_count = 0
            for task in active_tasks:
                logger.warning(f"Task '{task.task_id}' was in active state '{task.status}' during process crash/restart. Marking INTERRUPTED.")
                task.status = AgentStatus.INTERRUPTED.value
                task.updated_at = _utc_now_iso()
                task.recovery_status = "INTERRUPTED_ON_STARTUP"
                self.task_repo.update_task(task)

                # Record audit trajectory event
                self.audit_repo.record_event(
                    DBAuditEvent(
                        event_id=f"evt_rec_{task.task_id[:8]}_{int(datetime.now().timestamp())}",
                        task_id=task.task_id,
                        event_type="TASK_INTERRUPTED",
                        actor_id="system_recovery",
                        actor_role="SYSTEM",
                        component="recovery_manager",
                        status="INTERRUPTED",
                        metadata={"previous_status": task.status, "reason": "Process restart detected active task"},
                    )
                )
                interrupted_count += 1

            # 2. Count preserved WAITING_FOR_APPROVAL tasks
            waiting_tasks, _ = self.task_repo.list_tasks(status="WAITING_FOR_APPROVAL", limit=settings.TASK_LIST_MAX_LIMIT)
            waiting_count = len(waiting_tasks)

            logger.info(f"Startup recovery completed: {interrupted_count} tasks marked INTERRUPTED, {waiting_count} approval gates preserved.")

            return {
                "status": "SUCCESS",
                "interrupted_tasks_count": interrupted_count,
                "waiting_approval_count": waiting_count,
                "timestamp": _utc_now_iso(),
            }
        except Exception as exc:
            logger.error(f"Startup recovery failed: {exc}", exc_info=True)
            raise RecoveryFailedError(str(exc)) from exc

    def prepare_resume(self, task_id: str, actor_id: str = "operator") -> DBTask:
        """
        Validate and transition an INTERRUPTED task for controlled execution resume.
        """
        task = self.task_repo.get_task(task_id)
        if not task:
            raise TaskNotFoundError(task_id)

        if task.status != AgentStatus.INTERRUPTED.value:
            raise TaskNotResumableError(task_id, task.status)

        # Check if approval is still pending or required
        if task.requires_approval and task.approval_status != ApprovalStatus.APPROVED.value:
            task.status = AgentStatus.WAITING_FOR_APPROVAL.value
            task.updated_at = _utc_now_iso()
            task.recovery_status = "WAITING_APPROVAL_REVALIDATED"
            self.task_repo.update_task(task)

            self.audit_repo.record_event(
                DBAuditEvent(
                    event_id=f"evt_res_app_{task_id[:8]}_{int(datetime.now().timestamp())}",
                    task_id=task_id,
                    event_type="TASK_WAITING_FOR_APPROVAL",
                    actor_id=actor_id,
                    actor_role="OPERATOR",
                    component="recovery_manager",
                    status="WAITING_FOR_APPROVAL",
                    metadata={"reason": "Resume requires approval re-evaluation"},
                )
            )
            return task

        # Re-approve and transition to APPROVED for execution pickup
        TaskStateMachine.validate_transition(task_id, AgentStatus.INTERRUPTED, AgentStatus.APPROVED)
        task.status = AgentStatus.APPROVED.value
        task.updated_at = _utc_now_iso()
        task.recovery_status = "RESUMABLE_APPROVED"
        self.task_repo.update_task(task)

        self.audit_repo.record_event(
            DBAuditEvent(
                event_id=f"evt_res_ok_{task_id[:8]}_{int(datetime.now().timestamp())}",
                task_id=task_id,
                event_type="TASK_RECOVERY_STARTED",
                actor_id=actor_id,
                actor_role="OPERATOR",
                component="recovery_manager",
                status="APPROVED",
                metadata={"action": "Explicit resume initiated"},
            )
        )
        return task

    def prepare_retry(self, task_id: str, actor_id: str = "operator") -> DBTask:
        """
        Validate and prepare a FAILED task for retry execution if within max retry bounds.
        """
        task = self.task_repo.get_task(task_id)
        if not task:
            raise TaskNotFoundError(task_id)

        if task.status != AgentStatus.FAILED.value:
            raise TaskNotRetryableError(task_id, f"Task status is '{task.status}', expected FAILED.")

        # Check non-retryable error conditions (e.g. policy block or prohibited tools)
        if task.error_code in ("POLICY_VIOLATION", "PROHIBITED_TOOL", "AUTH_DENIED", "APPROVAL_REJECTED"):
            raise TaskNotRetryableError(task_id, f"Failure code '{task.error_code}' is non-retryable by security policy.")

        if task.retry_count >= task.max_retries:
            raise RetryLimitExceededError(task_id, task.retry_count, task.max_retries)

        task.retry_count += 1
        task.status = AgentStatus.APPROVED.value
        task.result_status = "RETRYING"
        task.updated_at = _utc_now_iso()
        task.error_code = None
        task.error_message = None
        task.recovery_status = f"RETRY_ATTEMPT_{task.retry_count}"
        self.task_repo.update_task(task)

        self.audit_repo.record_event(
            DBAuditEvent(
                event_id=f"evt_retry_{task_id[:8]}_{int(datetime.now().timestamp())}",
                task_id=task_id,
                event_type="TASK_RECOVERY_STARTED",
                actor_id=actor_id,
                actor_role="OPERATOR",
                component="recovery_manager",
                status="APPROVED",
                metadata={"retry_attempt": task.retry_count, "max_retries": task.max_retries},
            )
        )
        return task

    def get_recovery_stats(self) -> Dict[str, Any]:
        """Return recovery statistics."""
        interrupted, _ = self.task_repo.list_tasks(status="INTERRUPTED", limit=settings.TASK_LIST_MAX_LIMIT)
        waiting, _ = self.task_repo.list_tasks(status="WAITING_FOR_APPROVAL", limit=settings.TASK_LIST_MAX_LIMIT)
        failed, _ = self.task_repo.list_tasks(status="FAILED", limit=settings.TASK_LIST_MAX_LIMIT)

        return {
            "recovery_enabled": settings.AGENT_RECOVERY_ENABLED,
            "interrupted_tasks_count": len(interrupted),
            "waiting_approval_count": len(waiting),
            "failed_tasks_count": len(failed),
            "max_retries": settings.MAX_TASK_RETRIES,
        }
