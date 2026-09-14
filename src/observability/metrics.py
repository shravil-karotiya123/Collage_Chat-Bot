"""
In-Process Performance & Operational Metrics Collector.
"""

import threading
import time
from typing import Dict, Union

from config.settings import settings


class MetricsCollector:
    """
    Thread-safe in-process metrics store.
    Tracks requests, agent tasks, model inference operations, RAG queries, OCR, and security events.
    """

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self._lock = threading.Lock()
        self._counters: Dict[str, int] = {
            "http_requests_total": 0,
            "http_request_errors_total": 0,
            "agent_tasks_total": 0,
            "agent_tasks_failed_total": 0,
            "agent_tasks_completed_total": 0,
            "agent_tasks_pending_approval": 0,
            "agent_tool_calls_total": 0,
            "model_inference_total": 0,
            "model_inference_failures_total": 0,
            "rag_queries_total": 0,
            "rag_grounded_queries_total": 0,
            "ocr_requests_total": 0,
            "security_events_total": 0,
        }
        self._gauges: Dict[str, float] = {
            "vram_usage_mb": 0.0,
            "ram_usage_mb": 0.0,
            "active_tasks_count": 0.0,
        }

    def increment(self, name: str, amount: int = 1) -> None:
        """Increment specified counter metric."""
        if not self.enabled:
            return
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + amount

    def set_gauge(self, name: str, value: float) -> None:
        """Set specified gauge metric value."""
        if not self.enabled:
            return
        with self._lock:
            self._gauges[name] = float(value)

    def get_metrics(self) -> Dict[str, Union[int, float]]:
        """Retrieve snapshot of all recorded metrics."""
        with self._lock:
            merged = dict(self._counters)
            merged.update(self._gauges)
            return merged
