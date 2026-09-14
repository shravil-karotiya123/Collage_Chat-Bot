"""
Web UI Router for MRPL Sovereign AI Workbench.
Serves the single-page application index.html at root route GET /.
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(tags=["Web UI Operator Console"])

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent.parent / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.html"


@router.get(
    "/",
    response_class=FileResponse,
    summary="MRPL Sovereign AI Workbench Web UI Console",
    description="Serve local single-page application operator UI.",
)
async def serve_ui():
    """GET / endpoint serving local frontend operator console."""
    if not INDEX_FILE.exists():
        raise HTTPException(status_code=404, detail=f"Frontend index file not found at '{INDEX_FILE}'")
    return FileResponse(str(INDEX_FILE), media_type="text/html")
