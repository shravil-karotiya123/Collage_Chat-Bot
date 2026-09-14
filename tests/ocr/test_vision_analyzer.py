"""
Unit tests for VisionAnalyzer module.
"""

from unittest.mock import MagicMock
import pytest

from src.models.vision_manager import VisionManager
from src.ocr.image_processor import ProcessedImage
from src.ocr.vision_analyzer import VisionAnalyzer


@pytest.fixture
def mock_vision_manager() -> VisionManager:
    mock_model = MagicMock(spec=VisionManager)
    mock_model.model_name = "minicpm-v:8b"
    mock_model.analyze_image.return_value = "P&ID diagram showing CDU pump P-101 and valve V-20."
    return mock_model


def test_vision_analyzer_extract_text(mock_vision_manager: BaseModel) -> None:
    analyzer = VisionAnalyzer(vision_manager=mock_vision_manager)
    proc_img = ProcessedImage(
        filename="diagram.png",
        format="PNG",
        width=200,
        height=200,
        size_bytes=100,
        image_bytes=b"dummy image bytes",
    )

    text = analyzer.extract_text_from_image(proc_img)
    assert "CDU pump P-101" in text
    assert mock_vision_manager.analyze_image.called


def test_vision_analyzer_diagram_analysis(mock_vision_manager: BaseModel) -> None:
    analyzer = VisionAnalyzer(vision_manager=mock_vision_manager)
    proc_img = ProcessedImage(
        filename="schematic.png",
        format="PNG",
        width=300,
        height=300,
        size_bytes=200,
        image_bytes=b"dummy image bytes",
    )

    result = analyzer.analyze_diagram(proc_img)
    assert result["filename"] == "schematic.png"
    assert result["model_used"] == "minicpm-v:8b"
    assert "valve V-20" in result["visual_analysis"]
