"""
Unit tests for RAG REST API endpoints.
"""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import pytest

from src.api.app import app
from src.api.dependencies import get_rag_service
from src.models.base_model import BaseModel
from src.rag.embeddings import MockEmbeddingProvider
from src.rag.rag_service import RAGService
from src.rag.vector_store import MockVectorStore

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_rag_service_dependency() -> None:
    mock_qwen = MagicMock(spec=BaseModel)
    mock_qwen.model_name = "qwen2.5:7b"
    mock_qwen.generate.return_value = "The CDU operating temperature is 350C."

    fake_rag_service = RAGService(
        vector_store=MockVectorStore(),
        embedding_provider=MockEmbeddingProvider(),
        qwen_manager=mock_qwen,
    )

    app.dependency_overrides[get_rag_service] = lambda: fake_rag_service
    yield
    app.dependency_overrides.clear()


def test_api_index_document_endpoint() -> None:
    payload = {
        "filename": "manual.pdf",
        "file_hash": "hash_manual_123",
        "file_extension": ".pdf",
        "document_id": "doc_manual_01",
        "chunks": [
            {
                "chunk_id": 0,
                "content": "CDU unit operates at 350C.",
                "start_char": 0,
                "end_char": 25,
                "word_count": 5,
            }
        ],
    }

    response = client.post("/documents/index", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert data["status"] == "SUCCESS"
    assert data["document_id"] == "doc_manual_01"
    assert data["indexed_chunks_count"] == 1


def test_api_query_rag_endpoint() -> None:
    # 1. Index first
    client.post(
        "/documents/index",
        json={
            "filename": "manual.pdf",
            "file_hash": "hash123",
            "document_id": "doc_manual_01",
            "chunks": [
                {
                    "chunk_id": 0,
                    "content": "CDU unit operating temperature is 350C.",
                    "start_char": 0,
                    "end_char": 39,
                    "word_count": 6,
                }
            ],
        },
    )

    # 2. Query
    query_payload = {"query": "What is the CDU operating temperature?", "top_k": 2}
    response = client.post("/documents/query", json=query_payload)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert "350C" in data["answer"]
    assert len(data["sources"]) == 1
    assert data["sources"][0]["filename"] == "manual.pdf"


def test_api_delete_document_endpoint() -> None:
    client.post(
        "/documents/index",
        json={
            "filename": "delete_me.txt",
            "file_hash": "hash_del",
            "document_id": "doc_to_delete",
            "chunks": [{"chunk_id": 0, "content": "Text", "start_char": 0, "end_char": 4, "word_count": 1}],
        },
    )

    response = client.delete("/documents/doc_to_delete")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["deleted_chunks_count"] == 1


def test_api_rag_health_endpoint() -> None:
    response = client.get("/documents/rag/health")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["status"] == "healthy"
