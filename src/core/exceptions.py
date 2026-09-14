"""
Shared exception hierarchy for the workbench.
"""


class WorkbenchException(Exception):
    """Base exception for all domain errors within the AI Workbench."""

    pass


class ModelException(WorkbenchException):
    """Raised when model loading, initialization, or inference contracts fail."""

    pass


class VRAMExceededException(ModelException):
    """Raised when VRAM capacity (e.g., 8 GB RTX 5050 threshold) is exceeded."""

    pass


class SecurityException(WorkbenchException):
    """Raised when security boundaries or offline policies are breached."""

    pass


class SandboxException(WorkbenchException):
    """Raised when code execution sandbox policies or timeouts are violated."""

    pass


class ServiceException(WorkbenchException):
    """Raised when service layer operations fail."""

    pass
