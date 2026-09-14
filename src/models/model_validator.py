"""
Model Validator Utility for MRPL AI Workbench.
Verifies Ollama server reachability and local presence of configured production models.
"""

import logging
from typing import Any, Dict, List, Optional
import urllib.request
import json

from config.settings import settings

logger = logging.getLogger("MRPL.ModelValidator")


class ModelValidator:
    """
    Production Model & Runtime Validation Utility.
    Queries local Ollama endpoint to verify server availability and model presence
    without executing heavy LLM inference.
    """

    def __init__(self, ollama_url: Optional[str] = None) -> None:
        self.ollama_url = (ollama_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.required_models = [
            settings.DEFAULT_QWEN_MODEL,
            settings.DEFAULT_DEEPSEEK_MODEL,
            settings.DEFAULT_VISION_MODEL,
        ]

    def check_ollama_server(self, timeout: float = 3.0) -> bool:
        """
        Check if local Ollama server is online and accepting connections.
        """
        try:
            req = urllib.request.Request(f"{self.ollama_url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status == 200
        except Exception as exc:
            logger.warning(f"Ollama server reachability check failed ({self.ollama_url}): {exc}")
            return False

    def get_available_models(self, timeout: float = 3.0) -> List[str]:
        """
        Query Ollama server for currently installed local models.
        """
        try:
            req = urllib.request.Request(f"{self.ollama_url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    models = data.get("models", [])
                    return [m.get("name", "") for m in models if m.get("name")]
        except Exception as exc:
            logger.warning(f"Failed to fetch available models from Ollama: {exc}")
        return []

    def validate_models(self, timeout: float = 3.0) -> Dict[str, Any]:
        """
        Perform model validation across required production models.

        Returns:
            Dict detailing server status, required model presence, missing models, and health status.
        """
        server_available = self.check_ollama_server(timeout=timeout)
        if not server_available:
            return {
                "ollama_available": False,
                "models_status": {model: False for model in self.required_models},
                "missing_models": self.required_models,
                "configured_models": self.required_models,
                "all_installed_models": [],
                "validation_passed": False,
                "message": f"Ollama server unavailable at {self.ollama_url}",
            }

        installed_models = self.get_available_models(timeout=timeout)
        # Normalize model names (e.g. qwen2.5:7b matches qwen2.5:7b or qwen2.5:7b-instruct-q4_0)
        installed_names_lower = [m.lower() for m in installed_models]

        models_status = {}
        missing_models = []

        for req in self.required_models:
            req_lower = req.lower()
            req_base = req_lower.split(":")[0] if ":" in req_lower else req_lower

            # Exact or prefix match check
            is_present = any(
                req_lower == inst or inst.startswith(req_base) for inst in installed_names_lower
            )
            models_status[req] = is_present
            if not is_present:
                missing_models.append(req)

        validation_passed = len(missing_models) == 0

        return {
            "ollama_available": True,
            "models_status": models_status,
            "missing_models": missing_models,
            "configured_models": self.required_models,
            "all_installed_models": installed_models,
            "validation_passed": validation_passed,
            "message": "All required models validated"
            if validation_passed
            else f"Missing required models: {', '.join(missing_models)}",
        }

    def validate_local_models(self, timeout: float = 3.0) -> Dict[str, Any]:
        """
        Detailed offline validation exposing individual model status without downloading or executing inference.
        Classifies non-production models (e.g. llama3.2:1b) as non-production-installed-model.
        """
        raw_res = self.validate_models(timeout=timeout)
        installed = raw_res.get("all_installed_models", [])
        installed_lower = [m.lower() for m in installed]

        detailed_models = {}
        for req in self.required_models:
            is_present = raw_res.get("models_status", {}).get(req, False)
            detailed_models[req] = {
                "model_name": req,
                "installed": is_present,
                "available": is_present,
                "local": True,
                "runtime": settings.ACTIVE_RUNTIME,
                "status": "HEALTHY" if is_present else "MISSING",
                "classification": "production-model",
            }

        # Classify non-production installed models
        for inst in installed:
            inst_lower = inst.lower()
            inst_base = inst_lower.split(":")[0]
            if not any(req.lower().startswith(inst_base) for req in self.required_models):
                detailed_models[inst] = {
                    "model_name": inst,
                    "installed": True,
                    "available": True,
                    "local": True,
                    "runtime": settings.ACTIVE_RUNTIME,
                    "status": "NON_PRODUCTION",
                    "classification": "non-production-installed-model",
                }

        return {
            "status": "healthy" if raw_res["validation_passed"] else "degraded",
            "ollama_available": raw_res["ollama_available"],
            "production_models_validated": raw_res["validation_passed"],
            "models": detailed_models,
            "missing_models": raw_res["missing_models"],
        }
