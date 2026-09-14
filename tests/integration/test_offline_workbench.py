"""
Integration tests for offline WorkbenchService workflows and health telemetry.
"""

import pytest
from src.services.workbench_service import WorkbenchService


def test_offline_workbench_health():
    svc = WorkbenchService()
    health_resp = svc.health()

    assert health_resp.status in ("healthy", "degraded")
    assert health_resp.offline_status is not None
    assert health_resp.offline_status["offline_mode"] is True
    assert health_resp.offline_status["network_policy"] == "LOCAL_ONLY"
    assert health_resp.offline_status["ollama_local"] is True
