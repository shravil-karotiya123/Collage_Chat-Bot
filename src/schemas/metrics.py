"""
Metrics API Pydantic Schemas.
"""

from typing import Dict, Union
from pydantic import BaseModel, Field


class MetricValue(BaseModel):
    """Single metric measurement data point."""

    name: str = Field(..., description="Metric identifier key")
    value: Union[int, float] = Field(..., description="Numeric metric measurement")
    type: str = Field(..., description="Metric type (counter, gauge, histogram)")
    description: str = Field(..., description="Human readable description")


class MetricsResponse(BaseModel):
    """Aggregate metrics telemetry response model for GET /metrics."""

    status: str = Field(default="healthy", description="Metrics service status")
    timestamp: str = Field(..., description="Measurement collection ISO timestamp")
    metrics: Dict[str, Union[int, float]] = Field(..., description="Metric key-value pairs map")
