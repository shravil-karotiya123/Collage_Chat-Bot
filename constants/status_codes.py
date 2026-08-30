"""
System Status Codes & Enums.

Defines standardized status indicators across task execution, model routing,
tool execution, and error handling.
"""

from enum import Enum, auto


class TaskStatus(str, Enum):
    """Execution status of workbench tasks."""

    PENDING = "PENDING"
    ROUTING = "ROUTING"
    PROCESSING = "PROCESSING"
    MODEL_SWITCHING = "MODEL_SWITCHING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ModelStatus(str, Enum):
    """Status of local Ollama model in RAM/VRAM."""

    UNLOADED = "UNLOADED"
    LOADING = "LOADING"
    READY = "READY"
    UNLOADING = "UNLOADING"
    ERROR = "ERROR"


class ExecutionStatusCode(int, Enum):
    """Standardized numeric response code enums."""

    SUCCESS = 200
    INVALID_INPUT = 400
    MODEL_NOT_FOUND = 404
    RESOURCE_EXHAUSTED = 429
    MODEL_SWITCH_FAILED = 502
    EXECUTION_TIMEOUT = 504
    INTERNAL_ERROR = 500
