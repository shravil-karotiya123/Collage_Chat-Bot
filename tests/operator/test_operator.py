"""
Unit tests for Operator Console & System Telemetry Services.
"""

from src.operator.dashboard_service import DashboardService
from src.operator.operator_service import OperatorService
from src.operator.system_service import SystemService


def test_system_service_memory_and_vram_separation():
    sys_svc = SystemService()
    status = sys_svc.get_system_status()
    diag = sys_svc.get_memory_diagnostics()

    assert status["status"] == "healthy"
    assert "workbench_version" in status

    vram = diag["vram"]
    assert "allocated_vram_mb" in vram
    assert "configured_budget_mb" in vram
    # Verify configured VRAM budget is separated from physical telemetry
    assert vram["configured_budget_mb"] > 0


def test_operator_service_summaries():
    op_svc = OperatorService()

    models = op_svc.get_models_overview()
    assert models["ollama_status"] == "reachable"
    assert "qwen" in models["configured_models"]

    tasks = op_svc.get_tasks_summary()
    assert isinstance(tasks, list)


def test_operator_dashboard_rendering():
    op_svc = OperatorService()
    dash_svc = DashboardService(operator_service=op_svc)

    html = dash_svc.render_dashboard_html()

    assert "<!DOCTYPE html>" in html
    assert "MRPL AI WORKBENCH" in html
    assert "Operator Console" in html
