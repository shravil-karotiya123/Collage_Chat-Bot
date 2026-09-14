"""
FastAPI Dependency Injection providers module.
Centralizes object creation and injection for services, routers, and managers.
"""

from typing import Annotated
from fastapi import Depends

from src.routing.base_router import BaseRouter
from src.routing.router_factory import RouterFactory
from src.services.chat_service import ChatService


def get_model_router() -> BaseRouter:
    """
    Dependency provider returning configured BaseRouter instance.
    """
    return RouterFactory.create_router()


def get_chat_service(
    router: Annotated[BaseRouter, Depends(get_model_router)],
) -> ChatService:
    """
    Dependency provider returning ChatService initialized with injected BaseRouter.
    """
    return ChatService(router=router)


def get_document_pipeline() -> "DocumentProcessingPipeline":
    """
    Dependency provider returning DocumentProcessingPipeline instance.
    """
    from src.document_processing.pipeline import DocumentProcessingPipeline
    return DocumentProcessingPipeline()


def get_rag_service() -> "RAGService":
    """
    Dependency provider returning RAGService instance.
    """
    from src.rag.rag_service import RAGService
    return RAGService()


def get_ocr_service() -> "OCRService":
    """
    Dependency provider returning OCRService instance.
    """
    from src.ocr.ocr_service import OCRService
    return OCRService()


def get_workbench_service() -> "WorkbenchService":
    """
    Dependency provider returning unified WorkbenchService instance.
    """
    from src.services.workbench_service import WorkbenchService
    return WorkbenchService()


# Agent Subsystem Singletons
_global_state_store = None
_global_agent_orchestrator = None


def get_agent_state_store() -> "AgentStateStore":
    """
    Dependency provider returning singleton AgentStateStore instance.
    """
    global _global_state_store
    if _global_state_store is None:
        from config.settings import settings
        if settings.AGENT_PERSISTENCE_ENABLED:
            from src.agents.state_store import SQLiteAgentStateStore
            _global_state_store = SQLiteAgentStateStore()
        else:
            from src.agents.state_store import InMemoryAgentStateStore
            _global_state_store = InMemoryAgentStateStore()
    return _global_state_store


def get_agent_registry() -> "ToolRegistry":
    """
    Dependency provider returning ToolRegistry instance from global orchestrator.
    """
    orch = get_agent_orchestrator()
    return orch.registry


def get_agent_orchestrator() -> "AgentOrchestrator":
    """
    Dependency provider returning singleton AgentOrchestrator instance.
    """
    global _global_agent_orchestrator
    if _global_agent_orchestrator is None:
        from src.agents.orchestrator import AgentOrchestrator
        _global_agent_orchestrator = AgentOrchestrator(state_store=get_agent_state_store())
    return _global_agent_orchestrator


def get_network_policy() -> "NetworkPolicy":
    """
    Dependency provider returning NetworkPolicy instance.
    """
    from src.security.network_policy import NetworkPolicy
    return NetworkPolicy()


def get_offline_guard() -> "OfflineGuard":
    """
    Dependency provider returning OfflineGuard instance.
    """
    from src.security.offline_guard import OfflineGuard
    return OfflineGuard(network_policy=get_network_policy())


def get_startup_validator() -> "StartupValidator":
    """
    Dependency provider returning StartupValidator instance.
    """
    from src.security.startup_validator import StartupValidator
    return StartupValidator(offline_guard=get_offline_guard())

