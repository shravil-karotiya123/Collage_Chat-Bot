"""
Unit tests for OCR REST API endpoints and RAG Integration Contract.
"""

import io
from typing import Any, Tuple
from PIL import Image
from fastapi.testclient import TestClient
import pytest

from src.api.app import app
from src.api.dependencies import get_ocr_service, get_rag_service
from src.ocr.ocr_service import OCRService
from src.rag.embeddings import MockEmbeddingProvider
from src.rag.rag_service import RAGService
from src.rag.vector_store import MockVectorStore

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_dependencies() -> None:
    fake_ocr = OCRService()
    fake_rag = RAGService(
        vector_store=MockVectorStore(),
        embedding_provider=MockEmbeddingProvider(),
    )
    app.dependency_overrides[get_ocr_service] = lambda: fake_ocr
    app.dependency_overrides[get_rag_service] = lambda: fake_rag
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def dummy_image_file() -> Tuple[str, io.BytesIO, str]:
    img = Image.new("RGB", (50, 50), color="green")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ("scanned_receipt.png", buf, "image/png")


def test_api_ocr_process_endpoint(dummy_image_file: Any) -> None:
    filename, buf, content_type = dummy_image_file
    files = {"file": (filename, buf, content_type)}

    response = client.post("/ocr/process", files=files)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert data["status"] == "SUCCESS"
    assert data["filename"] == "scanned_receipt.png"
    assert data["ocr_pages_count"] == 1


def test_api_ocr_health_endpoint() -> None:
    response = client.get("/ocr/health")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["status"] == "healthy"
    assert res["data"]["ocr_enabled"] is True


def test_ocr_to_rag_integration_contract(dummy_image_file: Any) -> None:
    """
    Integration Contract: OCR output chunks pass directly into Phase 6 RAG Indexing.
    """
    filename, buf, content_type = dummy_image_file
    ocr_service = OCRService()
    rag_service = RAGService(
        vector_store=MockVectorStore(),
        embedding_provider=MockEmbeddingProvider(),
    )

    # 1. Process document via OCR Pipeline
    ocr_res = ocr_service.process_document(filename=filename, content_bytes=buf.getvalue())
    assert len(ocr_res.chunks) > 0

    # 2. Index generated OCR chunks directly into Phase 6 Vector Store
    rag_res = rag_service.index_document(
        filename=ocr_res.filename,
        file_hash=ocr_res.metadata["file_hash"],
        chunks=ocr_res.chunks,
        document_id=ocr_res.document_id,
    )

    assert rag_res["status"] == "SUCCESS"
    assert rag_res["document_id"] == ocr_res.document_id
    assert rag_res["indexed_chunks_count"] == len(ocr_res.chunks)
    assert rag_service.vector_store.count() == len(ocr_res.chunks)
