"""
Unit tests for Metrics, Structured Audit Event Logger, and Correlation ID Provider.
"""

from src.observability import (
    AuditLogger,
    MetricsCollector,
    generate_request_id,
    generate_task_id,
)


def test_correlation_id_generators():
    req_id = generate_request_id()
    task_id = generate_task_id()

    assert req_id.startswith("req_")
    assert task_id.startswith("task_")


def test_metrics_collector():
    metrics = MetricsCollector(enabled=True)

    metrics.increment("http_requests_total", 5)
    metrics.increment("agent_tasks_completed_total", 2)
    metrics.set_gauge("vram_usage_mb", 4096.0)

    m_map = metrics.get_metrics()

    assert m_map["http_requests_total"] == 5
    assert m_map["agent_tasks_completed_total"] == 2
    assert m_map["vram_usage_mb"] == 4096.0


def test_audit_event_logging_and_redaction():
    audit = AuditLogger(enabled=True)

    # Log event containing sensitive parameters to test redaction
    evt = audit.log_event(
        event_type="AUTH_LOGIN",
        request_id="req_123",
        actor_id="user_admin",
        severity="INFO",
        status="SUCCESS",
        metadata={
            "ip": "127.0.0.1",
            "password": "supersecretpassword",
            "token": "mrpl_tok_secret",
            "reasoning": "internal chain of thought reasoning text",
        },
    )

    assert evt["event_type"] == "AUTH_LOGIN"
    assert evt["request_id"] == "req_123"

    # Redaction checks
    meta = evt["metadata"]
    assert "password" not in meta
    assert "token" not in meta
    assert "reasoning" not in meta
    assert meta["ip"] == "127.0.0.1"

    # Retrieve events
    events = audit.get_events(event_type="AUTH_LOGIN")
    assert len(events) == 1
