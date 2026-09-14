"""
Observability package initializer.
"""

from src.observability.metrics import MetricsCollector
from src.observability.audit_events import AuditLogger
from src.observability.correlation import generate_request_id, generate_task_id

_metrics_instance: MetricsCollector = MetricsCollector()
_audit_logger_instance: AuditLogger = AuditLogger()


def get_metrics_collector() -> MetricsCollector:
    """Singleton provider for MetricsCollector."""
    return _metrics_instance


def get_audit_logger() -> AuditLogger:
    """Singleton provider for AuditLogger."""
    return _audit_logger_instance


__all__ = [
    "MetricsCollector",
    "AuditLogger",
    "generate_request_id",
    "generate_task_id",
    "get_metrics_collector",
    "get_audit_logger",
]
