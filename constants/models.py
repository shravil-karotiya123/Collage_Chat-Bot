"""
Supported Local Open-Weight LLM Definitions and Hardware Metadata.

Defines local model capabilities, RAM/VRAM constraints, and model routing roles
suitable for off-grid RTX 5050 GPU (16 GB system RAM) workstation execution.
"""

from enum import Enum
from typing import Any, Dict, List, TypedDict


class ModelCapability(str, Enum):
    """Capabilities supported by local open-weight models."""

    TEXT_GENERATION = "text_generation"
    CODE_EXECUTION = "code_execution"
    VISION_UNDERSTANDING = "vision_understanding"
    OCR_EXTRACTION = "ocr_extraction"
    EMBEDDING_GENERATION = "embedding_generation"
    ROUTING_REASONING = "routing_reasoning"
    DOCUMENT_ANALYSIS = "document_analysis"


class ModelSpec(TypedDict):
    """Structure defining a local model specification."""

    ollama_tag: str
    display_name: str
    capabilities: List[ModelCapability]
    parameter_size: str
    vram_required_mb: int
    ram_required_mb: int
    max_context_window: int
    is_multimodal: bool


# Supported Local Models Catalog
SUPPORTED_MODELS: Dict[str, ModelSpec] = {
    "llama3:8b": {
        "ollama_tag": "llama3:8b",
        "display_name": "Meta Llama 3 8B",
        "capabilities": [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.ROUTING_REASONING,
            ModelCapability.DOCUMENT_ANALYSIS,
        ],
        "parameter_size": "8B",
        "vram_required_mb": 5600,
        "ram_required_mb": 8192,
        "max_context_window": 8192,
        "is_multimodal": False,
    },
    "qwen2.5-coder:7b": {
        "ollama_tag": "qwen2.5-coder:7b",
        "display_name": "Qwen 2.5 Coder 7B",
        "capabilities": [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_EXECUTION,
            ModelCapability.ROUTING_REASONING,
        ],
        "parameter_size": "7B",
        "vram_required_mb": 5120,
        "ram_required_mb": 8192,
        "max_context_window": 32768,
        "is_multimodal": False,
    },
    "llava:7b": {
        "ollama_tag": "llava:7b",
        "display_name": "LLaVA Multimodal 7B",
        "capabilities": [
            ModelCapability.VISION_UNDERSTANDING,
            ModelCapability.OCR_EXTRACTION,
            ModelCapability.DOCUMENT_ANALYSIS,
        ],
        "parameter_size": "7B",
        "vram_required_mb": 5800,
        "ram_required_mb": 8192,
        "max_context_window": 4096,
        "is_multimodal": True,
    },
    "deepseek-r1:7b": {
        "ollama_tag": "deepseek-r1:7b",
        "display_name": "DeepSeek R1 Reasoning 7B",
        "capabilities": [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.ROUTING_REASONING,
        ],
        "parameter_size": "7B",
        "vram_required_mb": 5120,
        "ram_required_mb": 8192,
        "max_context_window": 16384,
        "is_multimodal": False,
    },
    "nomic-embed-text": {
        "ollama_tag": "nomic-embed-text",
        "display_name": "Nomic Embed Text (Local RAG)",
        "capabilities": [ModelCapability.EMBEDDING_GENERATION],
        "parameter_size": "137M",
        "vram_required_mb": 512,
        "ram_required_mb": 1024,
        "max_context_window": 8192,
        "is_multimodal": False,
    },
}

# Task-to-Model Role Mapping for Automatic Routing
MODEL_ROUTING_ROLES: Dict[str, str] = {
    "router": "qwen2.5-coder:7b",
    "general": "llama3:8b",
    "vision": "llava:7b",
    "code": "qwen2.5-coder:7b",
    "reasoning": "deepseek-r1:7b",
    "embedding": "nomic-embed-text",
}
