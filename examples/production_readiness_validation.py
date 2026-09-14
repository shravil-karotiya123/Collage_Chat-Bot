"""
Phase 11 Production Readiness & Live Ollama E2E Validation Script.
Verifies production readiness against local workstation hardware and Ollama LLM runtime.
"""

import asyncio
import os
import sys
import time
import urllib.request
import json
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings
from src.agents.orchestrator import AgentOrchestrator
from src.auth import AuthService, UserRole
from src.deployment.readiness import ReadinessChecker
from src.models.model_validator import ModelValidator
from src.observability import get_audit_logger, get_metrics_collector
from src.operator.system_service import SystemService
from src.services.workbench_service import WorkbenchService


async def run_production_validation():
    print("==================================================")
    print("PHASE 11 PRODUCTION READINESS & LIVE E2E VALIDATION")
    print("==================================================\n")

    # 1. Ollama Runtime Connectivity Check
    validator = ModelValidator()
    ollama_ok = validator.check_ollama_server()
    print(f"Ollama Server Available: {ollama_ok}")

    if not ollama_ok:
        print("[FAIL] Ollama server unavailable at http://127.0.0.1:11434")
        return 1

    # 2. Production Readiness Assessment
    checker = ReadinessChecker()
    readiness = checker.readiness_check()
    print(f"Deployment Readiness Assessment: {readiness['status']} (Ready: {readiness['ready']})")
    assert readiness["ready"] is True, "System readiness check failed"

    # 3. System Telemetry & Memory Diagnostics Check
    sys_svc = SystemService()
    sys_status = sys_svc.get_system_status()
    mem_diag = sys_svc.get_memory_diagnostics()
    print(f"System Uptime: {sys_status['uptime_seconds']}s | Version: {sys_status['workbench_version']}")
    print(f"RAM Used: {mem_diag['ram']['used_ram_mb']} / {mem_diag['ram']['configured_budget_mb']} MB")
    print(f"GPU VRAM Budget: {mem_diag['vram']['configured_budget_mb']} MB (GPU Device: {mem_diag['vram']['device_name']})")

    # 4. Local Authentication & RBAC Verification
    auth_svc = AuthService()
    admin_auth = auth_svc.authenticate_user("admin", "admin123")
    operator_auth = auth_svc.authenticate_user("operator", "operator123")

    assert admin_auth is not None and admin_auth[0].role == UserRole.ADMIN
    assert operator_auth is not None and operator_auth[0].role == UserRole.OPERATOR
    print("[PASS] Authentication & RBAC Local Credentials Validated")

    # 5. Live Workbench Agentic Execution Tests
    print("\n--------------------------------------------------")
    print("TEST 1: Qwen General Reasoning Agent Workflow")
    print("--------------------------------------------------")
    workbench = WorkbenchService()
    t1_start = time.perf_counter()
    chat_res = await workbench.ask_question("Explain refinery data sovereignty in one sentence.")
    t1_dur = time.perf_counter() - t1_start
    print(f"Model Used: {chat_res.selected_model}")
    print(f"Response: {chat_res.answer[:120]}...")
    print(f"Execution Time: {t1_dur:.2f}s")

    print("\n--------------------------------------------------")
    print("TEST 2: DeepSeek Coder Synthesis Workflow")
    print("--------------------------------------------------")
    t2_start = time.perf_counter()
    code_res = await workbench.ask_question("Write a Python function to calculate refinery throughput.")
    t2_dur = time.perf_counter() - t2_start
    print(f"Model Used: {code_res.selected_model}")
    print(f"Code Excerpt: {code_res.answer[:120]}...")
    print(f"Execution Time: {t2_dur:.2f}s")

    print("\n--------------------------------------------------")
    print("TEST 3: Agent Orchestrator & Approval Gate Workflow")
    print("--------------------------------------------------")
    orchestrator = AgentOrchestrator()
    state = orchestrator.create_agent_task("Prepare an approval note for budget sanction and send to management")
    print(f"Task Initial Status (Expect WAITING_FOR_APPROVAL): {state.agent_status.value}")
    assert state.agent_status.value == "WAITING_FOR_APPROVAL"

    # Approve task via operator gate
    orchestrator.approve(state.task_id, comment="Approved by MRPL Operator")
    executed_state = await orchestrator.execute(state.task_id)
    print(f"Post-Approval Execution Status: {executed_state.agent_status.value}")

    # 6. Observability Metrics & Audit Logging
    metrics = get_metrics_collector().get_metrics()
    audit_events = get_audit_logger().get_events(limit=5)
    print(f"\nCollected Metrics: Requests Total = {metrics.get('http_requests_total', 0)} | Audit Events Recorded = {len(audit_events)}")

    print("\n================================================================================")
    print("=== Phase 11 Production Validation PASSED ===")
    print("================================================================================")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run_production_validation()))
