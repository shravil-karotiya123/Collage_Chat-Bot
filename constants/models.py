"""
Supported Local Open-Weight LLM Definitions and Hardware Metadata.

Defines local model capabilities, RAM/VRAM constraints, and model routing roles
suitable for off-grid RTX 5050 GPU (16 GB system RAM) workstation execution.
Target Model Stack:
- Qwen2.5-7B-Instruct (Reasoning / Documents)
- Qwen2.5-Coder-7B-Instruct (Coding & Technical Tasks)
- Qwen2.5-VL-3B-Instruct (Multimodal Vision & Diagrams)
- PaddleOCR (Scanned PDFs & Text/Table Extraction)
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


# Target Local Models Catalog
SUPPORTED_MODELS: Dict[str, ModelSpec] = {
    "qwen2.5:7b": {
        "ollama_tag": "qwen2.5:7b-instruct",
        "display_name": "Qwen 2.5 7B Instruct (Q4_K_M)",
        "capabilities": [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.ROUTING_REASONING,
            ModelCapability.DOCUMENT_ANALYSIS,
        ],
        "parameter_size": "7B",
        "vram_required_mb": 4500,
        "ram_required_mb": 8192,
        "max_context_window": 32768,
        "is_multimodal": False,
    },
    "qwen2.5-coder:7b": {
        "ollama_tag": "qwen2.5-coder:7b-instruct",
        "display_name": "Qwen 2.5 Coder 7B Instruct (Q4_K_M)",
        "capabilities": [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_EXECUTION,
            ModelCapability.ROUTING_REASONING,
        ],
        "parameter_size": "7B",
        "vram_required_mb": 4500,
        "ram_required_mb": 8192,
        "max_context_window": 32768,
        "is_multimodal": False,
    },
    "qwen2.5-vl:3b": {
        "ollama_tag": "qwen2.5-vl:3b-instruct",
        "display_name": "Qwen 2.5 VL 3B Instruct",
        "capabilities": [
            ModelCapability.VISION_UNDERSTANDING,
            ModelCapability.OCR_EXTRACTION,
            ModelCapability.DOCUMENT_ANALYSIS,
        ],
        "parameter_size": "3B",
        "vram_required_mb": 2800,
        "ram_required_mb": 6144,
        "max_context_window": 16384,
        "is_multimodal": True,
    },
}

# Task-to-Model Role Mapping for Automatic Routing
MODEL_ROUTING_ROLES: Dict[str, str] = {
    "router": "qwen2.5:7b-instruct",
    "general": "qwen2.5:7b-instruct",
    "reasoning": "qwen2.5:7b-instruct",
    "document": "qwen2.5:7b-instruct",
    "summarization": "qwen2.5:7b-instruct",
    "code": "qwen2.5-coder:7b-instruct",
    "debugging": "qwen2.5-coder:7b-instruct",
    "sql": "qwen2.5-coder:7b-instruct",
    "vision": "qwen2.5-vl:3b-instruct",
    "diagram": "qwen2.5-vl:3b-instruct",
    "ocr": "paddleocr",
}
