"""
Integration tests for WorkbenchService orchestration layer.
"""

import io
from unittest.mock import MagicMock
from PIL import Image
import pytest

from src.models.base_model import BaseModel
from src.models.deepseek_manager import DeepSeekManager
from src.models.qwen_manager import QwenManager
from src.models.vision_manager import VisionManager
from src.rag.embeddings import MockEmbeddingProvider
from src.rag.rag_service import RAGService
from src.rag.vector_store import MockVectorStore
from src.routing.intent_classifier import UserIntent
from src.routing.model_router import ModelRouter
from src.routing.routing_rules import RoutingRules
from src.services.chat_service import ChatService
from src.services.workbench_service import WorkbenchService


@pytest.fixture
def mock_qwen() -> BaseModel:
    model = MagicMock(spec=QwenManager)
    model.model_name = "qwen2.5:7b"
    model.generate.return_value = "General Qwen assistant answer."
    model.health.return_value = {"loaded": True}
    return model


@pytest.fixture
def mock_deepseek() -> BaseModel:
    model = MagicMock(spec=DeepSeekManager)
    model.model_name = "deepseek-coder:6.7b"
    model.generate.return_value = "def quicksort(arr): return arr"
    model.health.return_value = {"loaded": True}
    return model


@pytest.fixture
def mock_vision() -> BaseModel:
    model = MagicMock(spec=VisionManager)
    model.model_name = "minicpm-v:8b"
    model.analyze_image.return_value = "Diagram shows valve V-101."
    model.generate.return_value = "Diagram shows valve V-101."
    model.health.return_value = {"loaded": True}
    return model


@pytest.fixture
def workbench_service(mock_qwen: BaseModel, mock_deepseek: BaseModel, mock_vision: BaseModel) -> WorkbenchService:
    rules = RoutingRules(
        custom_mappings={
            UserIntent.GENERAL_CHAT: mock_qwen,
            UserIntent.DOCUMENT: mock_qwen,
            UserIntent.APPROVAL_NOTE: mock_qwen,
            UserIntent.SUMMARIZATION: mock_qwen,
            UserIntent.CODING: mock_deepseek,
            UserIntent.DEBUGGING: mock_deepseek,
            UserIntent.IMAGE: mock_vision,
            UserIntent.OCR: mock_vision,
            UserIntent.DIAGRAM: mock_vision,
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
async def test_workflow_general_chat(workbench_service: WorkbenchService) -> None:
    res = await workbench_service.ask_question("What is an operational report?")
    assert res.status == "SUCCESS"
    assert res.selected_model == "qwen2.5:7b"
    assert "General Qwen" in res.answer


@pytest.mark.anyio
async def test_workflow_coding(workbench_service: WorkbenchService) -> None:
    res = await workbench_service.ask_question("Write a Python script to filter list items")
    assert res.status == "SUCCESS"
    assert res.selected_model == "deepseek-coder:6.7b"


@pytest.mark.anyio
async def test_workflow_debugging(workbench_service: WorkbenchService) -> None:
    res = await workbench_service.ask_question("Debug this Python IndexError stack trace")
    assert res.status == "SUCCESS"
    assert res.selected_model == "deepseek-coder:6.7b"


def test_workflow_document_ingestion_text(workbench_service: WorkbenchService) -> None:
    text_content = b"Refinery CDU unit operating manual section 1. Operating pressure is 15 bar."
    res = workbench_service.process_document(filename="cdu_manual.txt", content_bytes=text_content)
    assert res.status == "SUCCESS"
    assert res.extraction_mode == "text_parser"
    assert res.indexed_chunks_count > 0


def test_workflow_document_ingestion_scanned(workbench_service: WorkbenchService) -> None:
    img = Image.new("RGB", (50, 50), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    res = workbench_service.process_document(filename="scanned_diagram.png", content_bytes=buf.getvalue())
    assert res.status == "SUCCESS"
    assert res.extraction_mode == "ocr_vision"
    assert res.indexed_chunks_count > 0


@pytest.mark.anyio
async def test_workflow_rag_query_with_context(workbench_service: WorkbenchService) -> None:
    text_content = b"Refinery CDU unit operating pressure is 15 bar."
    workbench_service.process_document(filename="cdu_specs.txt", content_bytes=text_content)

    res = await workbench_service.ask_question("What is the CDU operating pressure?", force_rag=True)
    assert res.status == "SUCCESS"
    assert res.grounded_in_docs is True
    assert len(res.sources) > 0


@pytest.mark.anyio
async def test_workflow_rag_query_missing_context(workbench_service: WorkbenchService) -> None:
    res = await workbench_service.ask_question("What is the speed of light?", force_rag=True)
    assert res.status == "FALLBACK_NO_CONTEXT"
    assert res.grounded_in_docs is False
    assert "available documents do not contain sufficient information" in res.answer
    assert res.sources == []
