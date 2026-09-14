"""
Persistence Package Initialization.
Exports DatabaseManager, Repositories, Models, Retention, Backup, and Persistence Exceptions.
"""

from src.persistence.database import DatabaseManager, get_db_manager
from src.persistence.exceptions import (
    BackupFailedError,
    InvalidTaskStateError,
    PersistenceError,
    RecoveryFailedError,
    RetryLimitExceededError,
    TaskNotFoundError,
    TaskNotResumableError,
    TaskNotRetryableError,
    UnauthorizedTaskAccessError,
)
from src.persistence.models import DBAuditEvent, DBExecution, DBPlan, DBTask
from src.persistence.repositories import (
    AuditRepository,
    ExecutionRepository,
    TaskRepository,
    redact_sensitive_data,
    truncate_excerpt,
)
from src.persistence.retention import RetentionManager
from src.persistence.backup import PersistenceBackupManager

__all__ = [
    "DatabaseManager",
    "get_db_manager",
    "PersistenceError",
    "TaskNotFoundError",
    "InvalidTaskStateError",
    "TaskNotResumableError",
    "TaskNotRetryableError",
    "RetryLimitExceededError",
    "UnauthorizedTaskAccessError",
    "RecoveryFailedError",
    "BackupFailedError",
    "DBTask",
    "DBPlan",
    "DBExecution",
    "DBAuditEvent",
    "TaskRepository",
    "ExecutionRepository",
    "AuditRepository",
    "redact_sensitive_data",
    "truncate_excerpt",
    "RetentionManager",
    "PersistenceBackupManager",
]
