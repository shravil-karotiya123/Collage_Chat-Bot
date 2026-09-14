"""
Phase 9 End-to-End Functional Validation Script for MRPL AI Workbench.
Executes real end-to-end model workflows against active local Ollama service.
"""

import io
import os
import sys
import logging
from pathlib import Path
from PIL import Image, ImageDraw

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.models.model_validator import ModelValidator
from src.services.workbench_service import WorkbenchService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("MRPL.Phase9Validation")


def create_sample_test_image() -> bytes:
    """Generate a simple deterministic PNG diagram image for vision testing."""
    img = Image.new("RGB", (300, 150), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 280, 130], outline=(0, 51, 102), width=3)
    draw.text((40, 60), "MRPL CDU Valve V-101 Schema", fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


async def run_phase9_e2e_validation() -> None:
    logger.info("=================================================================")
    logger.info("=== Phase 9: Real End-to-End Functional Validation Starting ===")
    logger.info("=================================================================")

    # 1. Model Validation & Environment Audit
    validator = ModelValidator()
    val_res = validator.validate_models()
    logger.info(f"[1. MODEL VALIDATION] Ollama Server Online: {val_res['ollama_available']}")
    logger.info(f"[1. MODEL VALIDATION] Validation Passed: {val_res['validation_passed']}")
    logger.info(f"[1. MODEL VALIDATION] Models Status: {val_res['models_status']}")

    if not val_res["ollama_available"]:
        logger.warning("[SKIPPED REAL MODEL INFERENCE] Ollama server is offline at http://127.0.0.1:11434.")
        logger.warning("Real model functional tests require active Ollama server.")
        return

    service = WorkbenchService()

    # 2. Qwen Real Model Test
    logger.info("\n--- [2. QWEN REAL MODEL TEST] ---")
    qwen_query = "Explain what an approval note is in simple language."
    qwen_res = await service.ask_question(query=qwen_query)
    logger.info(f"Query: '{qwen_query}'")
    logger.info(f"Intent: {qwen_res.intent} | Model: {qwen_res.selected_model} | Status: {qwen_res.status}")
    logger.info(f"Response Snippet: {qwen_res.answer[:120]}...")
    assert qwen_res.status == "SUCCESS"
    assert qwen_res.selected_model in ("qwen2.5:7b", "qwen2.5:7b-instruct-q4_0")
    assert len(qwen_res.answer.strip()) > 0

    # 3. DeepSeek Coding Test
    logger.info("\n--- [3. DEEPSEEK CODING TEST] ---")
    code_query = "Write a Python function that validates an email address."
    code_res = await service.ask_question(query=code_query)
    logger.info(f"Query: '{code_query}'")
    logger.info(f"Intent: {code_res.intent} | Model: {code_res.selected_model} | Status: {code_res.status}")
    logger.info(f"Response Snippet: {code_res.answer[:120]}...")
    assert code_res.status == "SUCCESS"
    assert code_res.intent == "CODING"
    assert "deepseek" in code_res.selected_model.lower()
    assert len(code_res.answer.strip()) > 0

    # 4. DeepSeek Debugging Test
    logger.info("\n--- [4. DEEPSEEK DEBUGGING TEST] ---")
    debug_query = "Debug why this Python code fails:\nx = [1,2,3]\nprint(x[5])"
    debug_res = await service.ask_question(query=debug_query)
    logger.info(f"Query: '{debug_query}'")
    logger.info(f"Intent: {debug_res.intent} | Model: {debug_res.selected_model} | Status: {debug_res.status}")
    logger.info(f"Response Snippet: {debug_res.answer[:120]}...")
    assert debug_res.status == "SUCCESS"
    assert debug_res.intent in ("DEBUGGING", "CODING")
    assert "deepseek" in debug_res.selected_model.lower()
    assert len(debug_res.answer.strip()) > 0

    # 5. Vision Model Test
    logger.info("\n--- [5. VISION MULTIMODAL TEST] ---")
    img_bytes = create_sample_test_image()
    vision_res = service.process_image(image_bytes=img_bytes, filename="v101_schema.png", prompt="Inspect engineering diagram")
    logger.info(f"Filename: {vision_res.filename} | Model Used: {vision_res.model_used} | Status: {vision_res.status}")
    logger.info(f"Visual Analysis: {vision_res.visual_analysis[:120]}...")
    assert vision_res.status == "SUCCESS"
    assert "minicpm" in vision_res.model_used.lower()
    assert len(vision_res.visual_analysis.strip()) > 0

    # 6. Real Document Ingestion + Grounded RAG Test
    logger.info("\n--- [6. REAL DOCUMENT INGESTION & GROUNDED RAG TEST] ---")
    doc_path = BASE_DIR / "examples" / "data" / "workbench_test_document.txt"
    with open(doc_path, "rb") as f:
        doc_bytes = f.read()

    upload_res = service.process_document(filename="workbench_test_document.txt", content_bytes=doc_bytes, document_id="doc_workbench_001")
    logger.info(f"Uploaded: {upload_res.filename} | Document ID: {upload_res.document_id} | Chunks: {upload_res.indexed_chunks_count}")
    assert upload_res.status == "SUCCESS"
    assert upload_res.document_id == "doc_workbench_001"
    assert upload_res.indexed_chunks_count > 0

    rag_query = "What is the project code mentioned in the MRPL AI Workbench document?"
    rag_res = await service.ask_question(query=rag_query, document_id="doc_workbench_001", force_rag=True)
    logger.info(f"RAG Query: '{rag_query}'")
    logger.info(f"Grounded: {rag_res.grounded_in_docs} | Status: {rag_res.status} | Sources: {len(rag_res.sources)}")
    logger.info(f"Grounded Answer: {rag_res.answer[:150]}...")
    assert rag_res.status == "SUCCESS"
    assert rag_res.grounded_in_docs is True
    assert "MRPL-AI-001" in rag_res.answer
    assert len(rag_res.sources) > 0
    assert rag_res.sources[0].filename == "workbench_test_document.txt"

    # 7. RAG Negative Test (No Hallucination)
    logger.info("\n--- [7. RAG NEGATIVE NO-CONTEXT TEST] ---")
    neg_query = "What is the CEO's favorite programming language?"
    neg_res = await service.ask_question(query=neg_query, force_rag=True)
    logger.info(f"Negative Query: '{neg_query}'")
    logger.info(f"Grounded: {neg_res.grounded_in_docs} | Status: {neg_res.status}")
    logger.info(f"Response: {neg_res.answer}")
    assert neg_res.status == "FALLBACK_NO_CONTEXT"
    assert neg_res.grounded_in_docs is False
    assert "available documents do not contain sufficient information" in neg_res.answer

    # 8. Health Check Verification
    logger.info("\n--- [8. HEALTH TELEMETRY VERIFICATION] ---")
    health_res = service.health()
    logger.info(f"Workbench Status: {health_res.status} | Enabled: {health_res.workbench_enabled}")
    logger.info(f"Router Telemetry: {health_res.router_status}")
    logger.info(f"Memory Telemetry: {health_res.memory_status['model_lifecycle']}")
    assert health_res.status == "healthy"

    logger.info("\n=================================================================")
    logger.info("=== Phase 9 Real End-to-End Validation PASSED SUCCESSFULLY! ===")
    logger.info("=================================================================")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_phase9_e2e_validation())
