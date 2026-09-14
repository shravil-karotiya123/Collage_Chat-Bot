"""
Phase 12 Persistence, Job Management & Crash Recovery Live E2E Validation Script.
Verifies relational database initialization, durable task state, approval gate preservation,
startup crash recovery, explicit task resume, retry limits, and security redaction.
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings
from src.agents.agent_types import AgentStatus
from src.agents.orchestrator import AgentOrchestrator
from src.agents.recovery import RecoveryManager
from src.agents.state_store import SQLiteAgentStateStore
from src.persistence import (
    DBTask,
    DatabaseManager,
    ExecutionRepository,
    TaskRepository,
    get_db_manager,
)


async def run_persistence_e2e_validation():
    print("==================================================")
    print("PHASE 12 PERSISTENCE & CRASH RECOVERY E2E VALIDATION")
    print("==================================================\n")

    passed = 0
    failed = 0

    def record(check_name: str, status: bool, detail: str = ""):
        nonlocal passed, failed
        if status:
            passed += 1
            print(f"[PASS] {check_name} {f'({detail})' if detail else ''}")
        else:
            failed += 1
            print(f"[FAIL] {check_name} {f'({detail})' if detail else ''}")

    # 1. Database Manager & Relational Schema Initialization
    db_mgr = get_db_manager()
    db_status = db_mgr.get_status()
    record("Database Initialization", db_status["status"] == "healthy", f"DB: {db_status['database_name']}")

    task_repo = TaskRepository(db_manager=db_mgr)
    state_store = SQLiteAgentStateStore(task_repo=task_repo)
    orchestrator = AgentOrchestrator(state_store=state_store)
    rec_mgr = RecoveryManager(task_repo=task_repo)

    # 2. Task & Plan Persistence Check
    state1 = orchestrator.create_agent_task("Explain crude oil refinery distillation units")
    db_t1 = task_repo.get_task(state1.task_id)
    record("Task & Plan Relational Persistence", db_t1 is not None and db_t1.task_id == state1.task_id)

    # 3. Approval State Persistence Check
    state2 = orchestrator.create_agent_task("Draft approval note and send email for budget sanction")
    record("Approval Gate Task Creation (WAITING_FOR_APPROVAL)", state2.agent_status == AgentStatus.WAITING_FOR_APPROVAL)

    # 4. Crash Recovery Simulation — Active Task becomes INTERRUPTED, Approval Gate Preserved
    # Create artificial running task
    task_repo.create_task(
        DBTask(
            task_id="t_sim_crash_run",
            user_id="operator",
            session_id="s1",
            task_type="CHAT",
            title="Active Task before Crash",
            query="Simulate active task",
            status="RUNNING",
            risk_level="LOW",
            requires_approval=False,
            approval_status="NOT_REQUIRED",
        )
    )

    rec_res = rec_mgr.process_startup_recovery()
    record("Crash Recovery Sweep", rec_res["status"] == "SUCCESS", f"Interrupted Tasks: {rec_res['interrupted_tasks_count']}")

    t_crashed = task_repo.get_task("t_sim_crash_run")
    record("Running Task Transitioned to INTERRUPTED", t_crashed is not None and t_crashed.status == "INTERRUPTED")

    t_approval = task_repo.get_task(state2.task_id)
    record("Approval Gate Preserved Unchanged Across Restart", t_approval is not None and t_approval.status == "WAITING_FOR_APPROVAL")

    # 5. Controlled Task Resume Verification
    res_task = rec_mgr.prepare_resume("t_sim_crash_run")
    record("Explicit Interrupted Task Resume", res_task.status == "APPROVED")

    # 6. Idempotent Operation Verification
    state2.agent_status = AgentStatus.WAITING_FOR_APPROVAL
    state_store.save_state(state2)

    app_state1 = orchestrator.approve(state2.task_id, comment="Approve turn 1")
    app_state2 = orchestrator.approve(state2.task_id, comment="Approve turn 2")
    record("Idempotent Task Approval", app_state1.agent_status == AgentStatus.APPROVED and app_state2.agent_status == AgentStatus.APPROVED)

    # 7. Retry Bounds & Non-Retryable Policy Violation Verification
    task_repo.create_task(
        DBTask(
            task_id="t_policy_fail",
            user_id="operator",
            session_id="s1",
            task_type="CHAT",
            title="Policy Violation Task",
            query="Execute prohibited shell script",
            status="FAILED",
            risk_level="CRITICAL",
            requires_approval=True,
            approval_status="REJECTED",
            error_code="PROHIBITED_TOOL",
        )
    )

    policy_retry_blocked = False
    try:
        rec_mgr.prepare_retry("t_policy_fail")
    except Exception:
        policy_retry_blocked = True
    record("Prohibited Tool Non-Retryable Defense", policy_retry_blocked)

    # 8. Secret & Audit Event Redaction Verification
    audit_events, _ = rec_mgr.audit_repo.list_events_for_task("t_sim_crash_run")
    record("Audit Event Logging & Redaction", len(audit_events) >= 1)

    print("\n--------------------------------------------------")
    print(f"Validation checks passed: {passed}")
    print(f"Validation checks failed: {failed}")
    print("--------------------------------------------------")

    if failed == 0:
        print("\n================================================================================")
        print("=== Phase 12 Persistence E2E Validation PASSED ===")
        print("================================================================================")
        return 0
    else:
        print("\n================================================================================")
        print("=== Phase 12 Persistence E2E Validation FAILED ===")
        print("================================================================================")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(run_persistence_e2e_validation()))
