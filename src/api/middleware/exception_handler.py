"""
Global exception handling middleware and exception handlers for FastAPI backend.
Converts uncaught runtime errors and HTTP exceptions into standard API response JSON envelopes.
"""

import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.responses.standard_response import error_response

logger = logging.getLogger("MRPL.ExceptionHandler")


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on the FastAPI application instance."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        logger.warning(f"HTTPException [{exc.status_code}] on {request.url.path}: {exc.detail}")
        payload = error_response(
            message=str(exc.detail),
            status_code=exc.status_code,
            error={"detail": exc.detail},
        )
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
        payload = error_response(
            message="Input payload validation failed",
            status_code=422,
            error={"errors": exc.errors()},
        )
        return JSONResponse(status_code=422, content=payload.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled error on {request.url.path}: {str(exc)}", exc_info=True)
        payload = error_response(
            message="Internal server error encountered",
            status_code=500,
            error={"detail": str(exc)},
        )
        return JSONResponse(status_code=500, content=payload.model_dump())
