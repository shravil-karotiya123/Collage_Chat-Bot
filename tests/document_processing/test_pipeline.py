"""
Unit tests for DocumentProcessingPipeline end-to-end processing.
"""

from src.document_processing.pipeline import DocumentProcessingPipeline
from src.schemas.document import DocumentUploadResponse


def test_process_text_document_pipeline() -> None:
    pipeline = DocumentProcessingPipeline()
    content = b"MRPL AI Workbench Document Processing Pipeline Test.\nLine 2 text data."
    response = pipeline.process_document(file_name="test.txt", content=content)

    assert isinstance(response, DocumentUploadResponse)
    assert response.status == "SUCCESS"
    assert response.metadata.file_name == "test.txt"
    assert response.metadata.file_extension == ".txt"
    assert response.metadata.total_chunks > 0
    assert len(response.chunks) == response.metadata.total_chunks
    assert "MRPL AI Workbench" in response.chunks[0].content


def test_process_document_custom_chunking() -> None:
    pipeline = DocumentProcessingPipeline()
    content = b"A" * 1500  # 1500 characters
    response = pipeline.process_document(
        file_name="large.txt",
        content=content,
        chunk_size=500,
        chunk_overlap=50,
    )

    assert response.status == "SUCCESS"
    assert response.metadata.chunk_size == 500
    assert response.metadata.chunk_overlap == 50
    assert response.metadata.total_chunks >= 3
