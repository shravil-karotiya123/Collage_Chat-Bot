"""
Unit tests for CoderManager / DeepSeekManager legacy wrapper.
"""

import unittest
from unittest.mock import MagicMock
from src.models.deepseek_manager import DeepSeekManager
from src.models.runtime.base_runtime import BaseRuntime


class TestDeepSeekManager(unittest.TestCase):
    """Test suite verifying DeepSeekManager initialization, delegation, and metadata."""

    def setUp(self) -> None:
        self.mock_runtime = MagicMock(spec=BaseRuntime)
        self.mock_runtime.generate.return_value = "Reasoning step 1..."
        self.mock_runtime.health.return_value = {"available": True, "installed_models": ["qwen2.5-coder:7b-instruct"]}
        self.manager = DeepSeekManager(runtime=self.mock_runtime)

    def test_default_model_name(self) -> None:
        """Verify DeepSeekManager uses default Coder model tag."""
        self.assertIn("coder", self.manager.model_name.lower())

    def test_generate(self) -> None:
        """Verify DeepSeekManager generate() delegates to runtime."""
        result = self.manager.generate("Reason step by step")
        self.assertEqual(result, "Reasoning step 1...")
        self.mock_runtime.generate.assert_called_once()

    def test_metadata(self) -> None:
        """Verify DeepSeekManager get_metadata() returns architecture spec."""
        meta = self.manager.get_metadata()
        self.assertIn("coder", meta["family"].lower())
        self.assertIn("code_generation", meta["capabilities"])


if __name__ == "__main__":
    unittest.main()
