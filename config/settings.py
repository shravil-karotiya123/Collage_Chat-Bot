"""
Configuration Management Module.

Defines production settings using Pydantic BaseSettings.
All configuration parameters are loaded from environment variables or .env files,
supporting strict offline local execution constraints.
"""

import os
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base Directory Resolution
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Application Settings for Sovereign On-Premise Agentic AI Workbench.

    Configured specifically for local offline deployment on workstation hardware
    (RTX 5050 GPU, 16 GB RAM) running Ollama local models.
    """

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # --------------------------------------------------------------------------
    # System Identification & Environment
    # --------------------------------------------------------------------------
    PROJECT_NAME: str = Field(
        default="Sovereign On-Premise Agentic AI Workbench",
        description="Project title",
    )
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Deployment environment indicator",
    )
    DEBUG: bool = Field(
        default=True,
        description="Enable debug mode and extended logging",
    )

    # --------------------------------------------------------------------------
    # Local Model Server (Ollama) Settings
    # --------------------------------------------------------------------------
    OLLAMA_BASE_URL: str = Field(
        default="http://127.0.0.1:11434",
        description="Local Ollama server endpoint URL",
    )
    OLLAMA_TIMEOUT: float = Field(
        default=120.0,
        description="HTTP request timeout in seconds for local model execution",
    )
    MAX_CONCURRENT_MODELS: int = Field(
        default=1,
        description="Maximum models loaded into memory simultaneously (Strictly 1 for 16GB RAM limit)",
    )

    # --------------------------------------------------------------------------
    # Hardware & Resource Allocation Constraints
    # --------------------------------------------------------------------------
    MAX_VRAM_USAGE_MB: int = Field(
        default=7168,
        description="Maximum GPU VRAM budget in megabytes (RTX 5050 budget constraint)",
    )
    MAX_RAM_USAGE_MB: int = Field(
        default=12288,
        description="Maximum System RAM budget in megabytes (16 GB RAM setup)",
    )
    GPU_DEVICE_ID: int = Field(
        default=0,
        description="Target GPU index for CUDA operations",
    )

    # --------------------------------------------------------------------------
    # Default Model Names / Ollama Tags
    # --------------------------------------------------------------------------
    DEFAULT_ROUTER_MODEL: str = Field(
        default="qwen2.5-coder:7b",
        description="Default model used for request routing classification",
    )
    DEFAULT_VISION_MODEL: str = Field(
        default="llava:7b",
        description="Default model used for multimodal image/document vision analysis",
    )
    DEFAULT_RAG_MODEL: str = Field(
        default="llama3:8b",
        description="Default model used for local vector retrieval synthesis",
    )
    DEFAULT_GENERAL_MODEL: str = Field(
        default="llama3:8b",
        description="Default general purpose agentic reasoning model",
    )

    # --------------------------------------------------------------------------
    # Base Data Directory Paths
    # --------------------------------------------------------------------------
    LOG_DIR: Path = Field(
        default=BASE_DIR / "logs",
        description="Directory for application log output",
    )
    DOCUMENT_DIR: Path = Field(
        default=BASE_DIR / "documents",
        description="Directory for incoming raw document files",
    )
    OUTPUT_DIR: Path = Field(
        default=BASE_DIR / "outputs",
        description="Directory for generated reports, Word, and Excel artifacts",
    )
    DATABASE_DIR: Path = Field(
        default=BASE_DIR / "database",
        description="Directory for structured relational state storage",
    )
    VECTOR_STORE_DIR: Path = Field(
        default=BASE_DIR / "vector_store",
        description="Directory for local offline vector database index",
    )
    CACHE_DIR: Path = Field(
        default=BASE_DIR / "cache",
        description="Directory for transient computation caches",
    )
    DOWNLOAD_DIR: Path = Field(
        default=BASE_DIR / "downloads",
        description="Directory for local model downloads and temporary assets",
    )

    # --------------------------------------------------------------------------
    # Logging Configuration
    # --------------------------------------------------------------------------
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Log severity threshold (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    LOG_TO_CONSOLE: bool = Field(
        default=True,
        description="Enable standard stream console output",
    )
    LOG_TO_FILE: bool = Field(
        default=True,
        description="Enable persistent file log writing",
    )
    LOG_MAX_BYTES: int = Field(
        default=10 * 1024 * 1024,
        description="Maximum file size before rotating log files (10 MB default)",
    )
    LOG_BACKUP_COUNT: int = Field(
        default=5,
        description="Number of historical log backups to retain",
    )


# Instantiate Singleton Settings Object
settings = Settings()
