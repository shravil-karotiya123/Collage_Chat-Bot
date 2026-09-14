"""
Request Security & Rate Limiting Middleware.
"""

import time
import uuid
from typing import Callable, Optional
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config.settings import settings
from src.security.security_service import SecurityService

_security_service_instance: Optional[SecurityService] = None


def get_security_service() -> SecurityService:
    """Singleton provider for SecurityService."""
    global _security_service_instance
    if _security_service_instance is None:
        _security_service_instance = SecurityService()
    return _security_service_instance


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware injecting security headers, correlation IDs, process timing,
    and enforcing rate limits across incoming API requests.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()

        # 1. Inject or propagate X-Request-ID
        request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:10]}"
        request.state.request_id = request_id

        # 2. Rate Limiting Check
        sec_service = get_security_service()
        client_ip = request.client.host if request.client else "127.0.0.1"

        if settings.RATE_LIMIT_ENABLED and not request.url.path.startswith("/docs") and not request.url.path.startswith("/openapi.json"):
            allowed, remaining, reset_in = sec_service.rate_limiter.is_allowed(client_ip)
            if not allowed:
                sec_service.log_security_event(
                    event_type="RATE_LIMIT_EXCEEDED",
                    request_id=request_id,
                    severity="HIGH",
                    actor_id=client_ip,
                    details={"path": request.url.path, "reset_in_seconds": reset_in},
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "status": "ERROR",
                        "error": {
                            "code": 429,
                            "type": "RATE_LIMIT_EXCEEDED",
                            "message": f"Rate limit exceeded. Please retry in {reset_in:.1f} seconds.",
                        },
                        "request_id": request_id,
                    },
                    headers={
                        "Retry-After": str(int(reset_in) + 1),
                        "X-Request-ID": request_id,
                    },
                )

        # 3. Execute Request Processing Pipeline
        try:
            response = await call_next(request)
        except Exception as exc:
            import logging
            logging.getLogger("MRPL.Security.Middleware").error(f"[SECURITY MIDDLEWARE] Exception on {request.url.path}: {exc}", exc_info=True)
            exec_time_ms = (time.perf_counter() - start_time) * 1000
            sec_service.log_security_event(
                event_type="UNHANDLED_EXCEPTION",
                request_id=request_id,
                severity="HIGH",
                actor_id=client_ip,
                details={"error": str(exc), "path": request.url.path},
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "ERROR",
                    "error": {
                        "code": 500,
                        "type": "INTERNAL_SERVER_ERROR",
                        "message": "An internal server error occurred.",
                    },
                    "request_id": request_id,
                },
                headers={"X-Request-ID": request_id},
            )

        # 4. Attach Security Response Headers
        exec_time_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{exec_time_ms:.2f}ms"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"

        return response
