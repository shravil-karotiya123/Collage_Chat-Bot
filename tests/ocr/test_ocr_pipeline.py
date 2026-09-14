"""
Unit tests for OCRPipeline end-to-end processing.
"""

import io
from PIL import Image
import pytest

from src.ocr.ocr_pipeline import OCRPipeline
from src.schemas.ocr import OCRProcessResponse


@pytest.fixture
def sample_png_bytes() -> bytes:
    img = Image.new("RGB", (60, 60), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_ocr_pipeline_process_image(sample_png_bytes: bytes) -> None:
    pipeline = OCRPipeline()
    response = pipeline.process_document(
        filename="scanned_log.png",
        content_bytes=sample_png_bytes,
        chunk_size=500,
        chunk_overlap=50,
    )

    assert isinstance(response, OCRProcessResponse)
    assert response.status == "SUCCESS"
    assert response.filename == "scanned_log.png"
    assert response.total_pages == 1
    assert response.ocr_pages_count == 1
    assert len(response.pages) == 1
    assert response.pages[0].ocr_applied is True
    assert "file_hash" in response.metadata


def test_ocr_pipeline_invalid_empty_bytes() -> None:
    pipeline = OCRPipeline()
    with pytest.raises(ValueError, match="empty"):
        pipeline.process_document(filename="empty.pdf", content_bytes=b"")
