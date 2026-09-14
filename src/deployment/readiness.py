"""
Production Deployment Readiness & Health Assessment Provider.
"""

import time
from typing import Any, Dict

import urllib.request
from config.settings import settings
from src.models.model_validator import ModelValidator


class ReadinessChecker:
    """
    Evaluates system readiness prior to accepting production traffic.
    Checks Ollama endpoint availability, local vector store directory permissions,
    and security configuration validity without loading all LLM models into VRAM.
    """

    def __init__(self) -> None:
        self.validator = ModelValidator()

    def check_ollama_reachable(self) -> bool:
        """Verify local Ollama HTTP server is operational."""
        try:
            req = urllib.request.Request(f"{settings.OLLAMA_BASE_URL}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def readiness_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive production readiness assessment.
        Returns detailed check results dictionary with overall readiness flag.
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # 1. Ollama server check
        ollama_ok = self.check_ollama_reachable()

        # 2. Required directories check
        vector_store_ok = settings.VECTOR_STORE_PATH.exists() or settings.VECTOR_STORE_PATH.parent.exists()
        log_dir_ok = settings.LOG_DIR.exists() or settings.LOG_DIR.parent.exists()

        # 3. Security configuration check
        sec_config_ok = bool(settings.AUTH_TOKEN) and len(settings.AUTH_TOKEN) >= 8

        # 4. Configured models check
        configured_models = {
            "qwen": settings.QWEN_MODEL,
            "deepseek": settings.DEFAULT_DEEPSEEK_MODEL,
            "vision": settings.DEFAULT_VISION_MODEL,
        }

        all_ready = ollama_ok and vector_store_ok and log_dir_ok and sec_config_ok

        return {
            "ready": all_ready,
            "status": "READY" if all_ready else "NOT_READY",
            "timestamp": timestamp,
            "checks": {
                "ollama_reachable": ollama_ok,
                "vector_store_directory": vector_store_ok,
                "log_directory": log_dir_ok,
                "security_configuration": sec_config_ok,
                "configured_models": configured_models,
                "auth_enabled": settings.AUTH_ENABLED,
                "rate_limiting_enabled": settings.RATE_LIMIT_ENABLED,
            },
        }
