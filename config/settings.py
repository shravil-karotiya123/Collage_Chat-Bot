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
    ACTIVE_RUNTIME: str = Field(
        default="ollama",
        description="Active local inference engine (ollama, vllm, llamacpp, lmstudio)",
    )
    QWEN_MODEL: str = Field(
        default="qwen2.5:7b-instruct",
        description="Active Qwen2.5 7B Instruct local model tag (Q4_K_M)",
    )
    DEFAULT_QWEN_MODEL: str = Field(
        default="qwen2.5:7b-instruct",
        description="Default Qwen2.5 7B Instruct local model tag",
    )
    DEFAULT_DEEPSEEK_MODEL: str = Field(
        default="qwen2.5-coder:7b-instruct",
        description="Default Qwen2.5 Coder 7B Instruct local model tag (Q4_K_M)",
    )
    DEFAULT_CODER_MODEL: str = Field(
        default="qwen2.5-coder:7b-instruct",
        description="Default Qwen2.5 Coder 7B Instruct local model tag",
    )
    DEFAULT_ROUTER_MODEL: str = Field(
        default="qwen2.5:7b-instruct",
        description="Default model used for request routing classification",
    )
    DEFAULT_VISION_MODEL: str = Field(
        default="qwen2.5-vl:3b-instruct",
        description="Default model used for multimodal image/diagram vision analysis (Qwen2.5-VL-3B)",
    )
    DEFAULT_RAG_MODEL: str = Field(
        default="qwen2.5:7b-instruct",
        description="Default model used for local vector retrieval synthesis",
    )
    DEFAULT_GENERAL_MODEL: str = Field(
        default="qwen2.5:7b-instruct",
        description="Default general purpose agentic reasoning model",
    )

    # --------------------------------------------------------------------------
    # Model Routing Settings (Phase 3)
    # --------------------------------------------------------------------------
    DEFAULT_MODEL: str = Field(
        default="qwen2.5:7b-instruct",
        description="Default fallback model tag across workbench",
    )
    ROUTER_TYPE: str = Field(
        default="intent",
        description="Default router implementation type (intent, rule_based, default)",
    )
    ENABLE_CONFIDENCE: bool = Field(
        default=True,
        description="Enable intent classification confidence scoring",
    )
    ENABLE_ROUTING_LOGS: bool = Field(
        default=True,
        description="Enable structured telemetry logging for model routing",
    )

    # --------------------------------------------------------------------------
    # Document Processing Settings (Phase 5)
    # --------------------------------------------------------------------------
    DEFAULT_CHUNK_SIZE: int = Field(
        default=1000,
        description="Default text chunk character limit for document processing",
    )
    DEFAULT_CHUNK_OVERLAP: int = Field(
        default=200,
        description="Default character overlap between consecutive chunks",
    )
    MAX_DOCUMENT_SIZE_BYTES: int = Field(
        default=50 * 1024 * 1024,
        description="Maximum allowed upload document size in bytes (50 MB default)",
    )

    # --------------------------------------------------------------------------
    # Local RAG Subsystem Settings (Phase 6)
    # --------------------------------------------------------------------------
    RAG_ENABLED: bool = Field(
        default=True,
        description="Enable Local Retrieval-Augmented Generation subsystem",
    )
    EMBEDDING_MODEL: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Lightweight local CPU/GPU embedding model tag",
    )
    VECTOR_STORE_PATH: Path = Field(
        default=BASE_DIR / "data" / "chroma",
        description="Local persistent directory path for vector database index",
    )
    RAG_TOP_K: int = Field(
        default=3,
        description="Default number of relevant document chunks retrieved per RAG query",
    )
    MAX_RAG_CONTEXT: int = Field(
        default=3000,
        description="Maximum character context size passed to Qwen LLM prompt",
    )
    RAG_COLLECTION_NAME: str = Field(
        default="mrpl_documents",
        description="Default vector store collection name for document index",
    )

    # --------------------------------------------------------------------------
    # OCR & Vision Intelligence Settings (Phase 7)
    # --------------------------------------------------------------------------
    OCR_ENABLED: bool = Field(
        default=True,
        description="Enable OCR and scanned document processing subsystem",
    )
    OCR_ENGINE: str = Field(
        default="paddleocr",
        description="Default OCR extraction engine (paddleocr, vision_llm, hybrid)",
    )
    OCR_MAX_IMAGE_SIZE_MB: int = Field(
        default=20,
        description="Maximum allowed image size for OCR processing in megabytes",
    )
    OCR_MAX_PAGE_PIXELS: int = Field(
        default=2048 * 2048,
        description="Maximum resolution limit in total pixels for page images",
    )
    OCR_TIMEOUT: float = Field(
        default=60.0,
        description="Timeout in seconds for OCR image analysis operations",
    )
    VISION_ENABLED: bool = Field(
        default=True,
        description="Enable multimodal vision analysis for diagrams and schematics",
    )

    # --------------------------------------------------------------------------
    # Inference Hyperparameters & Runtime Config
    # --------------------------------------------------------------------------
    TEMPERATURE: float = Field(
        default=0.7,
        description="Default model sampling temperature",
    )
    TOP_P: float = Field(
        default=0.9,
        description="Default top-p nucleus sampling probability",
    )
    MAX_TOKENS: int = Field(
        default=2048,
        description="Maximum generation tokens per request",
    )
    GPU_ENABLED: bool = Field(
        default=True,
        description="Enable CUDA GPU acceleration",
    )

    @property
    def MODEL_CONFIG(self) -> dict:
        """
        Consolidated model runtime configuration dictionary.
        """
        return {
            "QWEN_MODEL": self.QWEN_MODEL,
            "runtime": self.ACTIVE_RUNTIME,
            "base_url": self.OLLAMA_BASE_URL,
            "timeout": self.OLLAMA_TIMEOUT,
            "gpu_enabled": self.GPU_ENABLED,
            "gpu_device_id": self.GPU_DEVICE_ID,
            "temperature": self.TEMPERATURE,
            "top_p": self.TOP_P,
            "max_tokens": self.MAX_TOKENS,
            "models": {
                "qwen": self.QWEN_MODEL,
                "deepseek": self.DEFAULT_DEEPSEEK_MODEL,
                "vision": self.DEFAULT_VISION_MODEL,
                "router": self.DEFAULT_ROUTER_MODEL,
                "rag": self.DEFAULT_RAG_MODEL,
                "general": self.DEFAULT_GENERAL_MODEL,
            },
        }


    # --------------------------------------------------------------------------
    # Base Data Directory Paths (6-Tier Sovereign Storage)
    # --------------------------------------------------------------------------
    DATA_DIR: Path = Field(
        default=BASE_DIR / "data",
        description="Root 6-tier sovereign data directory",
    )
    LOG_DIR: Path = Field(
        default=BASE_DIR / "logs",
        description="Directory for application log output",
    )
    DOCUMENT_DIR: Path = Field(
        default=BASE_DIR / "data" / "documents",
        description="Directory for incoming raw document files",
    )
    WORKSPACE_DIR: Path = Field(
        default=BASE_DIR / "data" / "workspaces",
        description="Directory for sovereign workspace state",
    )
    OUTPUT_DIR: Path = Field(
        default=BASE_DIR / "data" / "workspaces",
        description="Directory for generated reports, Word, and Excel artifacts",
    )
    DATABASE_DIR: Path = Field(
        default=BASE_DIR / "data" / "sqlite",
        description="Directory for structured relational state storage",
    )
    VECTOR_STORE_DIR: Path = Field(
        default=BASE_DIR / "data" / "chroma",
        description="Directory for local offline vector database index",
    )
    DUCKDB_DIR: Path = Field(
        default=BASE_DIR / "data" / "duckdb",
        description="Directory for local analytical telemetry database",
    )
    AUDIT_DIR: Path = Field(
        default=BASE_DIR / "data" / "audit",
        description="Directory for SHA-256 chained audit logs",
    )
    CACHE_DIR: Path = Field(
        default=BASE_DIR / "data" / "cache",
        description="Directory for transient computation caches",
    )
    DOWNLOAD_DIR: Path = Field(
        default=BASE_DIR / "data" / "downloads",
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

    # --------------------------------------------------------------------------
    # Agentic Orchestration Settings (Phase 10)
    # --------------------------------------------------------------------------
    AGENT_ENABLED: bool = Field(
        default=True,
        description="Enable Agentic Orchestration Subsystem",
    )
    AGENT_MAX_TASKS: int = Field(
        default=10,
        description="Maximum tasks allowed in a single agent plan execution",
    )
    AGENT_MAX_TOOL_CALLS: int = Field(
        default=10,
        description="Maximum total tool calls permitted per agent execution turn",
    )
    AGENT_MAX_EXECUTION_TIME: float = Field(
        default=300.0,
        description="Maximum execution timeout in seconds for agent workflow",
    )
    AGENT_AUTONOMOUS_EXECUTION: bool = Field(
        default=False,
        description="Toggle autonomous execution mode (strictly False in Phase 10)",
    )
    AGENT_REQUIRE_APPROVAL_FOR_MEDIUM_RISK: bool = Field(
        default=True,
        description="Require approval gate for medium risk operations",
    )
    AGENT_REQUIRE_APPROVAL_FOR_HIGH_RISK: bool = Field(
        default=True,
        description="Require approval gate for high risk operations",
    )
    AGENT_REQUIRE_APPROVAL_FOR_CRITICAL_RISK: bool = Field(
        default=True,
        description="Require approval gate for critical risk operations",
    )
    AGENT_STATE_BACKEND: str = Field(
        default="memory",
        description="Backend state persistence store (memory, sqlite)",
    )
    AGENT_AUDIT_ENABLED: bool = Field(
        default=True,
        description="Enable structured telemetry and audit event logging for agents",
    )

    # --------------------------------------------------------------------------
    # Security, Authentication & Governance Settings (Phase 11)
    # --------------------------------------------------------------------------
    AUTH_ENABLED: bool = Field(
        default=True,
        description="Enable Bearer token authentication and RBAC authorization",
    )
    AUTH_TOKEN: str = Field(
        default="mrpl_sovereign_secure_token_2026",
        description="Production authentication secret token",
    )
    AUTH_TOKEN_EXPIRY_SECONDS: int = Field(
        default=86400,
        description="Bearer token validity duration in seconds (24 hours)",
    )
    AUTH_REQUIRE_APPROVAL_ROLE: str = Field(
        default="OPERATOR",
        description="Minimum role required to approve agent tasks (OPERATOR, ADMIN)",
    )

    # --------------------------------------------------------------------------
    # Rate Limiting & Resource Control Settings (Phase 11)
    # --------------------------------------------------------------------------
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Enable in-process request rate limiting",
    )
    RATE_LIMIT_REQUESTS: int = Field(
        default=60,
        description="Maximum requests permitted within rate limit window",
    )
    RATE_LIMIT_WINDOW_SECONDS: int = Field(
        default=60,
        description="Sliding rate limit window in seconds",
    )
    AGENT_MAX_CONCURRENT_TASKS: int = Field(
        default=5,
        description="Maximum concurrent active agent tasks permitted",
    )

    # --------------------------------------------------------------------------
    # Observability, Metrics & Security Hardening (Phase 11)
    # --------------------------------------------------------------------------
    SECURITY_PROMPT_INJECTION_DETECTION: bool = Field(
        default=True,
        description="Enable detection and sanitization of prompt injection patterns",
    )
    AUDIT_ENABLED: bool = Field(
        default=True,
        description="Enable enterprise structured security audit event logging",
    )
    AUDIT_RETENTION_DAYS: int = Field(
        default=30,
        description="Retention duration for persistent audit log events",
    )
    METRICS_ENABLED: bool = Field(
        default=True,
        description="Enable in-process performance metrics collection",
    )
    OPERATOR_DASHBOARD_ENABLED: bool = Field(
        default=True,
        description="Enable server-rendered Operator Console dashboard",
    )
    BACKUP_ENABLED: bool = Field(
        default=True,
        description="Enable automated local vector store and audit backup subsystem",
    )
    BACKUP_PATH: Path = Field(
        default=BASE_DIR / "backups",
        description="Local directory path for system backups",
    )
    WORKBENCH_VERSION: str = Field(
        default="1.0.0",
        description="MRPL AI Workbench platform software version",
    )

    # --------------------------------------------------------------------------
    # Persistent Agent State & Job Management (Phase 12)
    # --------------------------------------------------------------------------
    AGENT_PERSISTENCE_ENABLED: bool = Field(
        default=True,
        description="Enable local persistent relational storage for agent state, plans, and audit history",
    )
    AGENT_DATABASE_PATH: Path = Field(
        default=BASE_DIR / "data" / "sqlite" / "mrpl_workbench.db",
        description="Local SQLite database file path for durable task management",
    )
    MAX_TASK_RETRIES: int = Field(
        default=2,
        description="Maximum retry attempts permitted for transient recoverable task failures",
    )
    MAX_PERSISTED_RESULT_CHARS: int = Field(
        default=4000,
        description="Maximum character limit for persisted task result excerpts",
    )
    TASK_HISTORY_RETENTION_DAYS: int = Field(
        default=30,
        description="Data retention period in days for completed/failed task history",
    )
    AGENT_RECOVERY_ENABLED: bool = Field(
        default=True,
        description="Enable startup crash recovery and interrupted task detection",
    )
    TASK_LIST_DEFAULT_LIMIT: int = Field(
        default=50,
        description="Default limit for paginated task lists",
    )
    TASK_LIST_MAX_LIMIT: int = Field(
        default=200,
        description="Maximum allowed limit for paginated task lists",
    )
    AUDIT_PAGE_DEFAULT_LIMIT: int = Field(
        default=50,
        description="Default page size for paginated audit log queries",
    )
    AUDIT_PAGE_MAX_LIMIT: int = Field(
        default=200,
        description="Maximum allowed page size for paginated audit log queries",
    )

    # --------------------------------------------------------------------------
    # Offline & Air-Gapped Production Hardening (Phase 13)
    # --------------------------------------------------------------------------
    OFFLINE_MODE: bool = Field(
        default=True,
        description="Enforce 100% offline air-gapped execution mode",
    )
    OFFLINE_STRICT_MODE: bool = Field(
        default=True,
        description="Strictly reject non-loopback endpoints and external cloud dependencies",
    )
    OLLAMA_HOST: str = Field(
        default="127.0.0.1",
        description="Host IP address for local Ollama runtime server",
    )
    OLLAMA_PORT: int = Field(
        default=11434,
        description="Port for local Ollama runtime server",
    )
    ALLOW_EXTERNAL_NETWORK: bool = Field(
        default=False,
        description="Allow outbound network calls (Strictly False for enterprise sovereignty)",
    )
    ALLOW_CLOUD_MODELS: bool = Field(
        default=False,
        description="Allow cloud-hosted AI inference services (Strictly False)",
    )
    ALLOW_REMOTE_EMBEDDINGS: bool = Field(
        default=False,
        description="Allow remote vector embedding services (Strictly False)",
    )
    ALLOW_REMOTE_VECTOR_STORE: bool = Field(
        default=False,
        description="Allow cloud vector store services (Strictly False)",
    )
    ALLOW_REMOTE_OCR: bool = Field(
        default=False,
        description="Allow cloud OCR APIs (Strictly False)",
    )
    OFFLINE_VALIDATION_ENABLED: bool = Field(
        default=True,
        description="Enable startup offline policy validation check",
    )
    OFFLINE_HEALTH_CHECK_ENABLED: bool = Field(
        default=True,
        description="Include offline posture telemetry in health check endpoints",
    )
    AIR_GAPPED_POLICY_VERSION: str = Field(
        default="1.0",
        description="Active air-gapped security policy framework version",
    )


# Instantiate Singleton Settings Object
settings = Settings()

