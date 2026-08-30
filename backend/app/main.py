"""
Main FastAPI Application Entrypoint for Render Deployment.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes.chat import router as chat_router
from app.routes.info import router as info_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Render-deployable Backend API for College Assistant Bot",
)

# Configure CORS Middleware for Vercel Frontend Interoperability
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://*.vercel.app",
    settings.FRONTEND_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production fallback for flexible Vercel preview URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(chat_router)
app.include_router(info_router)


@app.get("/health", tags=["Health Check"])
def health_check():
    """
    Health check endpoint utilized by Render monitoring.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "documentation": "/docs",
        "health_check": "/health",
    }
