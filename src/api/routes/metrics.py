"""
Metrics Telemetry API Router.
"""

import time
from fastapi import APIRouter
from src.observability import get_metrics_collector
from src.api.responses.standard_response import StandardResponse, success_response
from src.schemas.metrics import MetricsResponse

router = APIRouter(tags=["Metrics & Telemetry"])


@router.get("/metrics", response_model=StandardResponse[MetricsResponse])
async def get_metrics():
    """
    Retrieve current snapshot of operational system metrics.
    """
    collector = get_metrics_collector()
    metrics_data = collector.get_metrics()
    resp = MetricsResponse(
        status="healthy",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        metrics=metrics_data,
    )
    return success_response(data=resp, message="Metrics telemetry retrieved")
