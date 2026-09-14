"""
API Routes Package for MRPL AI Workbench REST API.
"""

from src.api.routes.chat import router as chat_router
from src.api.routes.documents import router as documents_router
from src.api.routes.health import router as health_router
from src.api.routes.models import router as models_router
from src.api.routes.ocr import router as ocr_router
from src.api.routes.rag import router as rag_router
from src.api.routes.router import router as router_info_router
from src.api.routes.workbench import router as workbench_router

__all__ = [
    "health_router",
    "models_router",
    "router_info_router",
    "chat_router",
    "documents_router",
    "rag_router",
    "ocr_router",
    "workbench_router",
]
