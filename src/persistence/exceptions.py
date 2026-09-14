"""
Domain exceptions for persistence, job management, and recovery.
"""


class PersistenceError(Exception):
    """Base exception for persistence failures."""

    def __init__(self, message: str, code: str = "PERSISTENCE_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class TaskNotFoundError(PersistenceError):
    """Raised when a target task ID does not exist in the database."""

    def __init__(self, task_id: str):
        super().__init__(f"Agent task '{task_id}' was not found.", code="TASK_NOT_FOUND")
        self.task_id = task_id


class InvalidTaskStateError(PersistenceError):
    """Raised when an illegal task state transition is requested."""

    def __init__(self, task_id: str, current_state: str, requested_state: str):
        super().__init__(
            f"Cannot transition task '{task_id}' from state '{current_state}' to '{requested_state}'.",
            code="INVALID_TASK_STATE",
        )
        self.task_id = task_id
        self.current_state = current_state
        self.requested_state = requested_state


class TaskNotResumableError(PersistenceError):
    """Raised when trying to resume a task that is not in INTERRUPTED state."""

    def __init__(self, task_id: str, current_state: str):
        super().__init__(
            f"Task '{task_id}' in state '{current_state}' cannot be resumed. Only INTERRUPTED tasks are resumable.",
            code="TASK_NOT_RESUMABLE",
        )
        self.task_id = task_id
        self.current_state = current_state


class TaskNotRetryableError(PersistenceError):
    """Raised when a failed task cannot be retried (e.g. policy violation or non-transient error)."""

    def __init__(self, task_id: str, reason: str):
        super().__init__(
            f"Task '{task_id}' cannot be retried: {reason}",
            code="TASK_NOT_RETRYABLE",
        )
        self.task_id = task_id
        self.reason = reason


class RetryLimitExceededError(PersistenceError):
    """Raised when maximum retry count for a task has been reached."""

    def __init__(self, task_id: str, retry_count: int, max_retries: int):
        super().__init__(
            f"Task '{task_id}' has exceeded maximum allowed retries ({retry_count}/{max_retries}).",
            code="RETRY_LIMIT_EXCEEDED",
        )
        self.task_id = task_id
        self.retry_count = retry_count
        self.max_retries = max_retries


class UnauthorizedTaskAccessError(PersistenceError):
    """Raised when a user attempts to access or mutate another user's task without RBAC permissions."""

    def __init__(self, task_id: str, user_id: str):
        super().__init__(
            f"User '{user_id}' is not authorized to access task '{task_id}'.",
            code="UNAUTHORIZED_TASK_ACCESS",
        )
        self.task_id = task_id
        self.user_id = user_id


class RecoveryFailedError(PersistenceError):
    """Raised when startup recovery processing fails."""

    def __init__(self, message: str):
        super().__init__(f"Task recovery processing failed: {message}", code="RECOVERY_FAILED")


class BackupFailedError(PersistenceError):
    """Raised when database backup archiving fails."""

    def __init__(self, message: str):
        super().__init__(f"Database backup failed: {message}", code="BACKUP_FAILED")
