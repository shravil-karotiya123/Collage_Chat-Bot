"""
Request logging middleware for MRPL AI Workbench REST API.
Emits structured telemetry for inbound HTTP requests and outbound responses.
"""

import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("MRPL.API")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware providing structured audit logging for all REST API transactions.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        start_time = time.perf_counter()
        client_host = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        logger.info(f"[HTTP INBOUND] {method} {path} | client={client_host}")

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000.0

            logger.info(
                f"[HTTP OUTBOUND] {method} {path} | status={response.status_code} | duration={duration_ms:.2f}ms"
            )
            return response
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(
                f"[HTTP FAILED] {method} {path} | error={str(exc)} | duration={duration_ms:.2f}ms"
            )
            raise exc
