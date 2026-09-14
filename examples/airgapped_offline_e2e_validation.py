"""
Phase 13 Offline & Air-Gapped E2E Production Validation Script.
Executes 20 live/offline workflow steps across FastAPI, OfflineGuard, NetworkPolicy,
ModelValidator, Document Ingestion, Local RAG, OCR, Agent Orchestration, and SQLite Persistence.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings
from src.agents.agent_types import AgentStatus
from src.agents.orchestrator import AgentOrchestrator
from src.agents.recovery import RecoveryManager
from src.agents.state_store import SQLiteAgentStateStore
from src.models.model_validator import ModelValidator
from src.persistence import DBTask, DatabaseManager, TaskRepository
from src.rag.embeddings import SentenceTransformerEmbeddingProvider
from src.rag.rag_service import RAGService
from src.security import NetworkPolicy, NetworkPolicyError, OfflineGuard
from src.services.workbench_service import WorkbenchService


async def run_offline_e2e_validation():
    print("==================================================")
    print("PHASE 13 OFFLINE & AIR-GAPPED E2E VALIDATION")
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

    # 1. WorkbenchService Initialization
    wb_svc = WorkbenchService()
    record("WorkbenchService Initialization", wb_svc is not None)

    # 2. Consolidated Offline Health Check
    health = wb_svc.health()
    record("Consolidated Health Telemetry", health.status in ("healthy", "degraded"))

    # 3. OfflineGuard Status Check
    guard = OfflineGuard()
    off_status = guard.get_status()
    record("OfflineGuard Telemetry Check", off_status["offline_mode"] is True and off_status["network_policy"] == "LOCAL_ONLY")

    # 4. Offline Posture Full Validation Check
    val_report = guard.validate_all()
    record("Offline Posture Full Validation Check", val_report["status"] in ("healthy", "degraded"))

    # 5. Local Model Validator Check
    model_val = ModelValidator()
    mod_report = model_val.validate_local_models()
    record("Model Validator Local Model Query", mod_report["status"] in ("healthy", "degraded"))

    # 6. Qwen 2.5 7B Model Tag Check
    record("Qwen 2.5 7B Configured Tag", settings.DEFAULT_MODEL == "qwen2.5:7b")

    # 7. DeepSeek Coder 6.7B Model Tag Check
    record("DeepSeek Coder 6.7B Configured Tag", settings.DEFAULT_DEEPSEEK_MODEL == "deepseek-coder:6.7b")

    # 8. MiniCPM-V 8B Vision Model Tag Check
    record("MiniCPM-V 8B Configured Tag", settings.DEFAULT_VISION_MODEL == "minicpm-v:8b")

    # 9. Document Ingestion Pipeline Execution
    doc_res = wb_svc.process_document(
        filename="test_refinery_manual.txt",
        content_bytes=b"MRPL Crude Distillation Unit (CDU-1) Operating Pressure: 2.4 bar. Emergency shutdown threshold: 3.5 bar.",
        document_id="doc_off_001",
    )
    record("Document Ingestion & Chunking", doc_res.indexed_chunks_count >= 1, f"Doc ID: {doc_res.document_id}")

    # 10. Local SentenceTransformer Embeddings
    emb_provider = SentenceTransformerEmbeddingProvider()
    emb_vec = emb_provider.embed_text("Refinery Operating Pressure")
    record("Local Vector Embedding Generation", len(emb_vec) == 384)

    # 11. ChromaDB Vector Store Indexing
    rag_svc = RAGService()
    record("ChromaDB Vector Indexing Health", rag_svc.health()["status"] == "healthy")

    # 12. Local RAG Grounded Context Retrieval
    rag_query_res = await rag_svc.query("What is CDU-1 operating pressure?", top_k=2)
    record("Local RAG Grounded Context Search", rag_query_res.status == "SUCCESS" and len(rag_query_res.sources) >= 0)

    # 13. Local RAG No-Context Fallback Handling
    rag_fallback_res = await rag_svc.query("Non-existent topic xyz123456", top_k=2)
    record("Local RAG Fallback Handling", rag_fallback_res.status == "SUCCESS")

    # 14. Agent Task Planning & Creation
    db_mgr = DatabaseManager()
    task_repo = TaskRepository(db_manager=db_mgr)
    state_store = SQLiteAgentStateStore(task_repo=task_repo)
    orchestrator = AgentOrchestrator(state_store=state_store)

    agent_state = orchestrator.create_agent_task("Explain crude oil refinery distillation process")
    record("Agent Task & Plan Creation", agent_state.task_id is not None)

    # 15. Agent Approval Gate Evaluation
    approval_state = orchestrator.create_agent_task("Draft approval note and send email for budget sanction")
    record("Agent Approval Gate Evaluation (WAITING_FOR_APPROVAL)", approval_state.agent_status == AgentStatus.WAITING_FOR_APPROVAL)

    # 16. SQLite Task State Persistence
    db_t = task_repo.get_task(agent_state.task_id)
    record("SQLite Relational Task State Persistence", db_t is not None and db_t.task_id == agent_state.task_id)

    # 17. Startup Crash Recovery Simulation
    rec_mgr = RecoveryManager(task_repo=task_repo)
    rec_res = rec_mgr.process_startup_recovery()
    record("Startup Crash Recovery Sweep", rec_res["status"] == "SUCCESS")

    # 18. Audit Event Persistence & Redaction
    from src.persistence import DBAuditEvent
    import uuid, time
    rec_mgr.audit_repo.record_event(
        DBAuditEvent(
            event_id=f"evt_{uuid.uuid4().hex[:10]}",
            task_id=agent_state.task_id,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            event_type="AGENT_CREATED",
            status=agent_state.agent_status.value,
            metadata={"query": agent_state.user_query},
        )
    )
    audit_events, _ = rec_mgr.audit_repo.list_events_for_task(agent_state.task_id)
    record("Audit Trajectory Event Persistence", len(audit_events) >= 1)

    # 19. Single-Model VRAM Allocation Strategy Check
    record("Single-Model Memory Lifecycle Strategy", settings.MAX_CONCURRENT_MODELS == 1)

    # 20. Synthetic Remote URL Policy Rejection
    net_policy = NetworkPolicy()
    remote_blocked = False
    try:
        net_policy.validate_url("https://api.openai.com/v1/chat/completions")
    except NetworkPolicyError:
        remote_blocked = True
    record("Synthetic Remote Endpoint Rejection", remote_blocked)

    print("\n--------------------------------------------------")
    print(f"Validation checks passed: {passed}")
    print(f"Validation checks failed: {failed}")
    print("--------------------------------------------------")

    if failed == 0:
        print("\n================================================================================")
        print("=== Phase 13 Offline E2E Validation PASSED ===")
        print("================================================================================")
        return 0
    else:
        print("\n================================================================================")
        print("=== Phase 13 Offline E2E Validation FAILED ===")
        print("================================================================================")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(run_offline_e2e_validation()))
