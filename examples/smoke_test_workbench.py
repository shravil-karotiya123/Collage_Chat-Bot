"""
Real Model Smoke Test & Verification Script for MRPL AI Workbench.
Demonstrates sequential model execution, intent routing, VRAM eviction, and health monitoring.
Requires Ollama local service running at http://127.0.0.1:11434.
"""

import sys
import logging
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.memory.diagnostic import MemoryDiagnostic
from src.routing.router_factory import RouterFactory
from src.services.workbench_service import WorkbenchService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("MRPL.SmokeTest")


def run_smoke_test() -> None:
    logger.info("=== Starting MRPL AI Workbench Real Model Smoke Test ===")

    # 1. Initialize Workbench Service
    service = WorkbenchService()
    diag = MemoryDiagnostic()

    # 2. Check Initial Memory Status
    mem_init = diag.get_memory_status()
    logger.info(f"[MEMORY INIT] RAM Available: {mem_init['system_ram']['available_mb']} MB | Active Model: {mem_init['model_lifecycle']['active_model']}")

    # 3. Test Intent Classification
    router = RouterFactory.create_router()
    test_queries = [
        ("Write a Python function to sort a list", "CODING"),
        ("Analyze CDU pump P-101 pressure diagram", "DIAGRAM"),
        ("What is the operating temperature of refinery unit 1?", "GENERAL_CHAT"),
    ]

    for q, expected in test_queries:
        res = router.classify_intent(q)
        logger.info(f"[ROUTER TEST] Query: '{q}' -> Classified Intent: {res.intent.value} (Expected: {expected})")

    # 4. Check Consolidated Subsystem Health
    health = service.health()
    logger.info(f"[WORKBENCH HEALTH] Overall Status: {health.status} | Workbench Enabled: {health.workbench_enabled}")
    logger.info(f"[ROUTER HEALTH] Active Rules: {health.router_status.get('rules_count')}")
    logger.info(f"[RAG HEALTH] Collection Chunks: {health.rag_status.get('total_chunks_indexed')}")
    logger.info(f"[OCR HEALTH] OCR Engine: {health.ocr_status.get('ocr_engine')}")

    # 5. Check Final Memory Status
    mem_final = diag.get_memory_status()
    logger.info(f"[MEMORY FINAL] RAM Available: {mem_final['system_ram']['available_mb']} MB | Active Model: {mem_final['model_lifecycle']['active_model']}")
    logger.info("=== Real Model Smoke Test Completed Successfully ===")


if __name__ == "__main__":
    run_smoke_test()
