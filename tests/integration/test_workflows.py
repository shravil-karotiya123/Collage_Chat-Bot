"""
End-to-end multi-step workflow integration tests for MRPL AI Workbench.
Verifies complete document ingestion -> chunking -> vector indexing -> grounded RAG QA lifecycle.
"""

import io
from unittest.mock import MagicMock
from PIL import Image
import pytest

from src.memory.diagnostic import MemoryDiagnostic
from src.models.qwen_manager import QwenManager
from src.rag.embeddings import MockEmbeddingProvider
from src.rag.rag_service import RAGService
from src.rag.vector_store import MockVectorStore
from src.routing.intent_classifier import UserIntent
from src.routing.model_router import ModelRouter
from src.routing.routing_rules import RoutingRules
from src.services.chat_service import ChatService
from src.services.workbench_service import WorkbenchService


@pytest.fixture
def integrated_service() -> WorkbenchService:
    mock_qwen = MagicMock(spec=QwenManager)
    mock_qwen.model_name = "qwen2.5:7b"
    mock_qwen.generate.return_value = "The refinery CDU unit operating pressure is 15 bar as specified in doc."

    rules = RoutingRules(
        custom_mappings={
            UserIntent.GENERAL_CHAT: mock_qwen,
            UserIntent.DOCUMENT: mock_qwen,
            UserIntent.APPROVAL_NOTE: mock_qwen,
            UserIntent.SUMMARIZATION: mock_qwen,
            UserIntent.UNKNOWN: mock_qwen,
        }
    )
    router = ModelRouter(rules=rules)
    chat_svc = ChatService(router=router)

    store = MockVectorStore()
    embedding = MockEmbeddingProvider()
    rag = RAGService(vector_store=store, embedding_provider=embedding, qwen_manager=mock_qwen)

    return WorkbenchService(
        router=router,
        chat_service=chat_svc,
        rag_service=rag,
    )


@pytest.mark.anyio
async def test_full_document_ingestion_to_rag_workflow(integrated_service: WorkbenchService) -> None:
    # 1. User uploads document
    doc_bytes = b"MRPL Refinery CDU Unit Technical Specification. Operating pressure is 15 bar. Temperature limit is 380C."
    upload_res = integrated_service.process_document(
        filename="mrpl_cdu_spec.txt",
        content_bytes=doc_bytes,
        document_id="doc_cdu_101",
    )

    assert upload_res.status == "SUCCESS"
    assert upload_res.document_id == "doc_cdu_101"
    assert upload_res.indexed_chunks_count > 0

    # 2. User asks question targeting indexed document
    chat_res = await integrated_service.ask_question(
        query="What is the operating pressure of the CDU unit?",
        force_rag=True,
    )

    assert chat_res.status == "SUCCESS"
    assert chat_res.grounded_in_docs is True
    assert "15 bar" in chat_res.answer
    assert len(chat_res.sources) > 0
    assert chat_res.sources[0].filename == "mrpl_cdu_spec.txt"


def test_memory_diagnostic_telemetry() -> None:
    diag = MemoryDiagnostic()
    status = diag.get_memory_status()
    assert status["status"] == "healthy"
    assert "system_ram" in status
    assert "process_memory" in status
    assert "gpu" in status
    assert "model_lifecycle" in status
