"""
Request timing middleware.
Measures total HTTP request processing duration and attaches telemetry headers.
"""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware measuring request execution time and attaching performance metrics.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time_ms = (time.perf_counter() - start_time) * 1000.0

        response.headers["X-Process-Time"] = f"{process_time_ms:.2f}ms"
        response.headers["X-Response-Time-Sec"] = f"{process_time_ms / 1000.0:.4f}s"
        return response
