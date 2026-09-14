"""
Unit tests for BaseOCR abstraction interface.
"""

from typing import Any, Dict
from src.ocr.base_ocr import BaseOCR


class ConcreteTestOCR(BaseOCR):
    def process_image(self, image_bytes: bytes, filename: str, **kwargs: Any) -> Dict[str, Any]:
        return {"text": "extracted text", "confidence": 0.95, "method": "test_ocr"}

    def process_page(self, page_bytes: bytes, page_number: int, **kwargs: Any) -> Dict[str, Any]:
        return {"text": "page text", "page_number": page_number}

    def health(self) -> Dict[str, Any]:
        return {"status": "ok"}


def test_base_ocr_subclass_contract() -> None:
    ocr = ConcreteTestOCR()
    assert ocr.health()["status"] == "ok"
    res = ocr.process_image(b"dummy image bytes", "test.png")
    assert res["text"] == "extracted text"
    page_res = ocr.process_page(b"page bytes", 1)
    assert page_res["page_number"] == 1
