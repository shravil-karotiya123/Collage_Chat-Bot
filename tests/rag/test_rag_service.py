"""
Unit tests for RAGService orchestration layer.
"""

from unittest.mock import MagicMock
import pytest

from src.models.base_model import BaseModel
from src.rag.embeddings import MockEmbeddingProvider
from src.rag.rag_service import RAGService
from src.rag.vector_store import MockVectorStore
from src.schemas.document import DocumentChunkSchema


@pytest.fixture
def mock_qwen() -> BaseModel:
    mock_model = MagicMock(spec=BaseModel)
    mock_model.model_name = "qwen2.5:7b"
    mock_model.generate.return_value = "The CDU unit operates at 350 degrees Celsius based on refinery.pdf."
    mock_model.health.return_value = {"loaded": True, "available": True}
    return mock_model


@pytest.fixture
def rag_service(mock_qwen: BaseModel) -> RAGService:
    store = MockVectorStore()
    embedding = MockEmbeddingProvider()
    return RAGService(
        vector_store=store,
        embedding_provider=embedding,
        qwen_manager=mock_qwen,
    )


@pytest.mark.anyio
async def test_rag_service_index_and_query(rag_service: RAGService, mock_qwen: BaseModel) -> None:
    chunks = [
        DocumentChunkSchema(
            chunk_id=0,
            content="CDU unit operating temperature is 350 degrees Celsius.",
            start_char=0,
            end_char=54,
            word_count=8,
        )
    ]

    # Index
    index_res = rag_service.index_document(
        filename="refinery.pdf",
        file_hash="hash_cdu",
        chunks=chunks,
        document_id="doc_cdu_spec",
    )
    assert index_res["status"] == "SUCCESS"
    assert index_res["indexed_chunks_count"] == 1

    # Query
    query_res = await rag_service.query("What is the CDU operating temperature?")
    assert query_res.status == "SUCCESS"
    assert "350 degrees Celsius" in query_res.answer
    assert len(query_res.sources) == 1
    assert query_res.sources[0].filename == "refinery.pdf"
    assert mock_qwen.generate.called


@pytest.mark.anyio
async def test_rag_service_missing_context_behavior(rag_service: RAGService, mock_qwen: BaseModel) -> None:
    # Query empty vector store
    mock_qwen.generate.reset_mock()
    query_res = await rag_service.query("What is the speed of light?")

    assert query_res.status == "FALLBACK_NO_CONTEXT"
    assert "available documents do not contain sufficient information" in query_res.answer
    assert query_res.sources == []
    # Must NOT call Qwen LLM when context is missing/empty!
    assert not mock_qwen.generate.called


def test_rag_service_delete_document(rag_service: RAGService) -> None:
    chunks = [DocumentChunkSchema(chunk_id=0, content="Test text", start_char=0, end_char=9, word_count=2)]
    rag_service.index_document(filename="test.txt", file_hash="hash1", chunks=chunks, document_id="doc_del")
    assert rag_service.vector_store.count() == 1

    deleted = rag_service.delete_document("doc_del")
    assert deleted == 1
    assert rag_service.vector_store.count() == 0


def test_rag_service_health(rag_service: RAGService) -> None:
    h = rag_service.health()
    assert h["status"] == "healthy"
    assert h["rag_enabled"] is True
    assert "embedding_provider" in h
    assert "vector_store" in h
