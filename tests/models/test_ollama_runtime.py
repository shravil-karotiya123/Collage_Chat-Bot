"""
Unit tests for OllamaRuntime with mocked ollama API client.
"""

import unittest
from unittest.mock import MagicMock, patch
from src.models.runtime.ollama_runtime import OllamaRuntime


class TestOllamaRuntime(unittest.TestCase):
    """Test suite verifying OllamaRuntime method calls with mocked ollama client."""

    @patch("src.models.runtime.ollama_runtime.OLLAMA_AVAILABLE", True)
    @patch("src.models.runtime.ollama_runtime.ollama")
    def test_load_model(self, mock_ollama_module: MagicMock) -> None:
        """Verify load_model triggers generate with warm-up prompt."""
        mock_client = MagicMock()
        mock_ollama_module.Client.return_value = mock_client

        runtime = OllamaRuntime()
        success = runtime.load_model("qwen2.5-coder:7b")

        self.assertTrue(success)
        mock_client.generate.assert_called_once_with(
            model="qwen2.5-coder:7b",
            prompt="",
            keep_alive="10m",
        )

    @patch("src.models.runtime.ollama_runtime.OLLAMA_AVAILABLE", True)
    @patch("src.models.runtime.ollama_runtime.ollama")
    def test_unload_model(self, mock_ollama_module: MagicMock) -> None:
        """Verify unload_model triggers generate with keep_alive=0."""
        mock_client = MagicMock()
        mock_ollama_module.Client.return_value = mock_client

        runtime = OllamaRuntime()
        success = runtime.unload_model("qwen2.5-coder:7b")

        self.assertTrue(success)
        mock_client.generate.assert_called_once_with(
            model="qwen2.5-coder:7b",
            prompt="",
            keep_alive=0,
        )

    @patch("src.models.runtime.ollama_runtime.OLLAMA_AVAILABLE", True)
    @patch("src.models.runtime.ollama_runtime.ollama")
    def test_generate(self, mock_ollama_module: MagicMock) -> None:
        """Verify generate delegates to client.generate and extracts response text."""
        mock_client = MagicMock()
        mock_client.generate.return_value = {"response": "Refinery status OK"}
        mock_ollama_module.Client.return_value = mock_client

        runtime = OllamaRuntime()
        output = runtime.generate("Status check", "llama3:8b")

        self.assertEqual(output, "Refinery status OK")
        mock_client.generate.assert_called_once()

    @patch("src.models.runtime.ollama_runtime.OLLAMA_AVAILABLE", True)
    @patch("src.models.runtime.ollama_runtime.ollama")
    def test_list_models(self, mock_ollama_module: MagicMock) -> None:
        """Verify list_models extracts model tag names."""
        mock_client = MagicMock()
        mock_client.list.return_value = {
            "models": [
                {"name": "qwen2.5-coder:7b"},
                {"name": "llama3:8b"},
            ]
        }
        mock_ollama_module.Client.return_value = mock_client

        runtime = OllamaRuntime()
        models = runtime.list_models()

        self.assertEqual(models, ["qwen2.5-coder:7b", "llama3:8b"])


if __name__ == "__main__":
    unittest.main()
