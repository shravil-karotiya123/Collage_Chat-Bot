"""
Unit tests for Qwen 2.5 7B model integration (QwenManager).
"""

import unittest
from unittest.mock import MagicMock
from src.models.qwen_manager import QwenManager
from src.models.runtime.base_runtime import BaseRuntime


class TestQwenIntegration(unittest.TestCase):
    """
    Test suite verifying QwenManager interaction with BaseRuntime interface.
    """

    def setUp(self) -> None:
        self.mock_runtime = MagicMock(spec=BaseRuntime)
        self.mock_runtime.load_model.return_value = True
        self.mock_runtime.unload_model.return_value = True
        self.mock_runtime.generate.return_value = (
            "An approval note is a formal document used in corporate or technical operations "
            "to request official authorization for an action, expenditure, or policy change."
        )
        self.mock_runtime.health.return_value = {
            "runtime": "ollama",
            "available": True,
            "models_count": 1,
            "installed_models": ["qwen2.5:7b"],
            "gpu_enabled": True,
        }

        self.qwen_manager = QwenManager(model_name="qwen2.5:7b", runtime=self.mock_runtime)

    def test_load_qwen_model(self) -> None:
        """Verify load() delegates to BaseRuntime and sets loaded state."""
        success = self.qwen_manager.load()
        self.assertTrue(success)
        self.assertTrue(self.qwen_manager.is_loaded)
        self.mock_runtime.load_model.assert_called_once_with("qwen2.5:7b")

    def test_generate_qwen_response(self) -> None:
        """Verify generate() delegates prompt to BaseRuntime."""
        prompt = "Explain what an approval note is."
        response = self.qwen_manager.generate(prompt)

        self.assertIn("approval note", response.lower())
        self.mock_runtime.generate.assert_called_once_with(
            prompt=prompt,
            model_name="qwen2.5:7b",
        )

    def test_health_check_qwen(self) -> None:
        """Verify health() returns structured status indicating model availability."""
        health_status = self.qwen_manager.health()

        self.assertEqual(health_status["model_name"], "qwen2.5:7b")
        self.assertTrue(health_status["available"])
        self.assertTrue(health_status["model_exists"])
        self.assertEqual(health_status["runtime_status"]["runtime"], "ollama")

    def test_unload_qwen_model(self) -> None:
        """Verify unload() delegates to BaseRuntime and clears loaded state."""
        self.qwen_manager.is_loaded = True
        success = self.qwen_manager.unload()

        self.assertTrue(success)
        self.assertFalse(self.qwen_manager.is_loaded)
        self.mock_runtime.unload_model.assert_called_once_with("qwen2.5:7b")


if __name__ == "__main__":
    unittest.main()
