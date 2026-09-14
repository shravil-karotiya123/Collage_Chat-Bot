"""
Unit tests for TextOCREngine module with PaddleOCR support.
"""

import io
from PIL import Image
import pytest

from src.ocr.text_ocr import TextOCREngine


@pytest.fixture
def image_bytes() -> bytes:
    img = Image.new("RGB", (50, 50), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_text_ocr_engine_process_image(image_bytes: bytes) -> None:
    engine = TextOCREngine()
    res = engine.process_image(image_bytes, "scanned_doc.png")

    assert "text" in res
    assert "word_count" in res
    assert "char_count" in res
    assert res["method"] in {"ocr_fallback", "paddleocr", "vision_llm"}
    assert res["confidence"] >= 0.90


def test_text_ocr_engine_health() -> None:
    engine = TextOCREngine()
    h = engine.health()
    assert h["engine"] == "TextOCREngine"
    assert h["status"] == "ready"
