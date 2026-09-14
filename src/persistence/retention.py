"""
Data Retention Management Subsystem.
Purges expired task, execution, and audit log records while protecting active/recoverable tasks.
"""

from datetime import datetime, timedelta, timezone
import logging
from typing import Any, Dict, Optional

from config.settings import settings
from src.persistence.database import DatabaseManager, get_db_manager

logger = logging.getLogger("MRPL.Persistence.Retention")

PROTECTED_STATUSES = ("CREATED", "PLANNING", "WAITING_FOR_APPROVAL", "RUNNING", "INTERRUPTED")


class RetentionManager:
    """
    Purges historical task, execution, and audit records older than retention period.
    """

    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        retention_days: Optional[int] = None,
    ) -> None:
        self.db = db_manager or get_db_manager()
        self.retention_days = retention_days or settings.TASK_HISTORY_RETENTION_DAYS

    def purge_expired_records(self) -> Dict[str, Any]:
        """
        Execute retention cleanup query.
        """
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=self.retention_days)).isoformat()
        logger.info(f"Executing retention purge for records older than cutoff: {cutoff_date}")

        protected_placeholders = ", ".join(["?"] * len(PROTECTED_STATUSES))

        # Query expired task IDs
        sql_find_expired = f"""
            SELECT task_id FROM agent_tasks
            WHERE created_at < ? AND status NOT IN ({protected_placeholders});
        """
        params_find = [cutoff_date] + list(PROTECTED_STATUSES)

        conn = self.db.get_raw_connection()
        cursor = conn.execute(sql_find_expired, tuple(params_find))
        expired_task_ids = [r["task_id"] for r in cursor.fetchall()]

        if not expired_task_ids:
            logger.info("No expired task records found for deletion.")
            return {
                "status": "SUCCESS",
                "cutoff_date": cutoff_date,
                "purged_tasks_count": 0,
                "purged_executions_count": 0,
                "purged_audit_events_count": 0,
            }

        task_id_placeholders = ", ".join(["?"] * len(expired_task_ids))

        # Perform atomic deletions
        with self.db.transaction() as conn_tx:
            cursor_del_exec = conn_tx.execute(
                f"DELETE FROM agent_executions WHERE task_id IN ({task_id_placeholders});",
                tuple(expired_task_ids),
            )
            purged_execs = cursor_del_exec.rowcount

            cursor_del_audit = conn_tx.execute(
                f"DELETE FROM agent_audit_events WHERE task_id IN ({task_id_placeholders});",
                tuple(expired_task_ids),
            )
            purged_audit = cursor_del_audit.rowcount

            cursor_del_plans = conn_tx.execute(
                f"DELETE FROM agent_plans WHERE task_id IN ({task_id_placeholders});",
                tuple(expired_task_ids),
            )

            cursor_del_tasks = conn_tx.execute(
                f"DELETE FROM agent_tasks WHERE task_id IN ({task_id_placeholders});",
                tuple(expired_task_ids),
            )
            purged_tasks = cursor_del_tasks.rowcount

        logger.info(
            f"Retention purge complete: {purged_tasks} tasks, {purged_execs} executions, {purged_audit} audit events deleted."
        )

        return {
            "status": "SUCCESS",
            "cutoff_date": cutoff_date,
            "purged_tasks_count": purged_tasks,
            "purged_executions_count": purged_execs,
            "purged_audit_events_count": purged_audit,
        }
