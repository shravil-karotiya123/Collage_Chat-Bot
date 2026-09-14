"""
Unit tests for VisionManager model manager.
"""

import unittest
from unittest.mock import MagicMock
from src.models.vision_manager import VisionManager
from src.models.runtime.base_runtime import BaseRuntime


class TestVisionManager(unittest.TestCase):
    """Test suite verifying VisionManager initialization, image analysis, and metadata."""

    def setUp(self) -> None:
        self.mock_runtime = MagicMock(spec=BaseRuntime)
        self.mock_runtime.generate.return_value = "Image shows refinery piping schematics."
        self.mock_runtime.health.return_value = {"available": True, "installed_models": ["qwen2.5-vl:3b-instruct"]}
        self.manager = VisionManager(runtime=self.mock_runtime)

    def test_default_model_name(self) -> None:
        """Verify VisionManager uses default vision model tag."""
        model_name = self.manager.model_name.lower()
        self.assertTrue("vl" in model_name or "vision" in model_name or "minicpm" in model_name)

    def test_analyze_image(self) -> None:
        """Verify VisionManager analyze_image() delegates combined prompt to runtime."""
        result = self.manager.analyze_image("documents/diagram.png", "Describe piping")
        self.assertEqual(result, "Image shows refinery piping schematics.")
        self.mock_runtime.generate.assert_called_once()

    def test_metadata(self) -> None:
        """Verify VisionManager get_metadata() returns architecture spec."""
        meta = self.manager.get_metadata()
        self.assertEqual(meta["family"], "vision_multimodal")
        self.assertIn("ocr", meta["capabilities"])


if __name__ == "__main__":
    unittest.main()
