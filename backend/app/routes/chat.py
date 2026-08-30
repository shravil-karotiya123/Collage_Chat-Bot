"""
Chat Route Handlers.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.bot_service import bot_service

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("")
def handle_chat(request: ChatRequest):
    response = bot_service.process_query(request.message)
    return response
