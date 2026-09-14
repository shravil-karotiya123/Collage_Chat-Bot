"""
Unit tests for POST /chat API endpoint with mocked runtime inference.
"""

from unittest.mock import patch
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


from config.settings import settings


def test_post_chat_coding_query() -> None:
    with patch("src.models.runtime.ollama_runtime.OllamaRuntime.generate") as mock_gen:
        mock_gen.return_value = "def sort_list(arr):\n    return sorted(arr)"
        response = client.post(
            "/chat",
            json={"query": "Write a python function to sort a list", "temperature": 0.5},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True
        data = payload["data"]
        assert "def sort_list" in data["text"]
        assert data["model_used"] == settings.DEFAULT_CODER_MODEL
        assert data["intent"] == "CODING"


def test_post_chat_general_query() -> None:
    with patch("src.models.runtime.ollama_runtime.OllamaRuntime.generate") as mock_gen:
        mock_gen.return_value = "MRPL AI Workbench is a sovereign local agent platform."
        response = client.post(
            "/chat",
            json={"query": "Hello, what is MRPL AI Workbench?"},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True
        data = payload["data"]
        assert data["model_used"] == settings.QWEN_MODEL
        assert data["intent"] == "GENERAL_CHAT"


def test_post_chat_vision_query() -> None:
    with patch("src.models.runtime.ollama_runtime.OllamaRuntime.generate") as mock_gen:
        mock_gen.return_value = "Piping schematic diagram identified."
        response = client.post(
            "/chat",
            json={
                "query": "Inspect this diagram schematic",
                "context": {"image_path": "refinery.png", "has_image": True},
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True
        data = payload["data"]
        assert data["model_used"] == settings.DEFAULT_VISION_MODEL
        assert data["intent"] in {"IMAGE", "OCR", "DIAGRAM"}


def test_post_chat_validation_error() -> None:
    response = client.post("/chat", json={"query": ""})
    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
    assert payload["status_code"] == 422
