"""
Unit tests for QwenManager model manager.
"""

import unittest
from unittest.mock import MagicMock
from src.models.qwen_manager import QwenManager
from src.models.runtime.base_runtime import BaseRuntime


class TestQwenManager(unittest.TestCase):
    """Test suite verifying QwenManager initialization, delegation, and metadata."""

    def setUp(self) -> None:
        self.mock_runtime = MagicMock(spec=BaseRuntime)
        self.mock_runtime.generate.return_value = "def hello(): pass"
        self.mock_runtime.health.return_value = {"available": True, "installed_models": ["qwen2.5-coder:7b"]}
        self.manager = QwenManager(runtime=self.mock_runtime)

    def test_default_model_name(self) -> None:
        """Verify QwenManager uses default Qwen model tag."""
        self.assertIn("qwen", self.manager.model_name.lower())

    def test_generate(self) -> None:
        """Verify QwenManager generate() delegates to runtime."""
        result = self.manager.generate("Write a function")
        self.assertEqual(result, "def hello(): pass")
        self.mock_runtime.generate.assert_called_once()

    def test_metadata(self) -> None:
        """Verify QwenManager get_metadata() returns architecture spec."""
        meta = self.manager.get_metadata()
        self.assertEqual(meta["family"], "qwen")
        self.assertIn("code", meta["capabilities"])


if __name__ == "__main__":
    unittest.main()
