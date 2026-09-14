"""
Unit tests for ModelValidator module.
"""

from unittest.mock import MagicMock, patch
import pytest

from src.models.model_validator import ModelValidator
from config.settings import settings


def test_model_validator_server_unavailable() -> None:
    validator = ModelValidator()
    with patch("urllib.request.urlopen", side_effect=Exception("Connection refused")):
        res = validator.validate_models()
        assert res["ollama_available"] is False
        assert res["validation_passed"] is False
        assert len(res["missing_models"]) == 3


def test_model_validator_all_models_present() -> None:
    validator = ModelValidator()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = (
        b'{"models": [{"name": "qwen2.5:7b-instruct"}, {"name": "qwen2.5-coder:7b-instruct"}, {"name": "qwen2.5-vl:3b-instruct"}]}'
    )
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = validator.validate_models()
        assert res["ollama_available"] is True
        assert res["validation_passed"] is True
        assert res["missing_models"] == []
        assert res["models_status"][settings.DEFAULT_QWEN_MODEL] is True
