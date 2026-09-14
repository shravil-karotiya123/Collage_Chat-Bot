"""
Unit tests for OCRService business logic layer.
"""

import io
from unittest.mock import MagicMock
from PIL import Image
import pytest

from src.models.vision_manager import VisionManager
from src.ocr.ocr_service import OCRService
from src.ocr.vision_analyzer import VisionAnalyzer


@pytest.fixture
def image_bytes() -> bytes:
    img = Image.new("RGB", (40, 40), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def mock_vision_analyzer() -> VisionAnalyzer:
    mock_vm = MagicMock(spec=VisionManager)
    mock_vm.model_name = "minicpm-v:8b"
    mock_vm.analyze_image.return_value = "Mock visual analysis output"
    return VisionAnalyzer(vision_manager=mock_vm)


def test_ocr_service_process_document(image_bytes: bytes) -> None:
    service = OCRService()
    res = service.process_document(filename="scan.png", content_bytes=image_bytes)
    assert res.status == "SUCCESS"
    assert res.filename == "scan.png"


def test_ocr_service_process_image(image_bytes: bytes, mock_vision_analyzer: VisionAnalyzer) -> None:
    service = OCRService(vision_analyzer=mock_vision_analyzer)
    res = service.process_image(image_bytes=image_bytes, filename="diagram.png")
    assert res["filename"] == "diagram.png"
    assert "visual_analysis" in res
    assert res["visual_analysis"] == "Mock visual analysis output"


def test_ocr_service_health() -> None:
    service = OCRService()
    h = service.health()
    assert h["status"] == "healthy"
    assert h["ocr_enabled"] is True
    assert "vision_model" in h
