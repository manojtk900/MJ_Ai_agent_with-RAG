"""
ML Routes — FastAPI endpoints for Local Intent Classification, NER, and Latency Benchmarking.
"""
from typing import Any, Dict, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agents.ml_router import benchmark_latency, route_command

router = APIRouter(prefix="/ml")


class MLRouteRequest(BaseModel):
    message: str = Field(..., description="User voice or text command", example="open youtube and search trending yash songs")
    confidence_threshold: Optional[float] = Field(default=0.80, ge=0.0, le=1.0, description="Minimum confidence threshold for routing")


class MLRouteResponse(BaseModel):
    intent: str = Field(..., description="Predicted intent label", example="youtube_search")
    confidence: float = Field(..., description="Classification probability score", example=0.9985)
    entities: Dict[str, str] = Field(default_factory=dict, description="Extracted named entities", example={"query": "trending yash songs"})


class MLBenchmarkResponse(BaseModel):
    intent_latency_ms: float = Field(..., description="Intent classifier inference latency in ms")
    entity_latency_ms: float = Field(..., description="Entity extractor inference latency in ms")
    total_latency_ms: float = Field(..., description="Total command routing latency in ms")
    device: str = Field(default="cpu", description="Compute device (CPU / CUDA)")
    status: str = Field(default="optimal", description="Operational health status")


@router.post("/route", response_model=MLRouteResponse, summary="Route User Command via Local ML")
async def route_user_command(request: MLRouteRequest):
    """
    Classify user input into intent and extract named entities using fine-tuned DistilBERT models.
    Executes in under 50ms without making external LLM API calls.
    """
    result = route_command(request.message, confidence_threshold=request.confidence_threshold or 0.80)
    return MLRouteResponse(
        intent=result["intent"],
        confidence=result["confidence"],
        entities=result["entities"],
    )


@router.get("/benchmark", response_model=MLBenchmarkResponse, summary="Benchmark Local ML Inference Latency")
async def get_ml_benchmark():
    """
    Run latency benchmark on local DistilBERT models and return sub-component execution metrics.
    """
    metrics = benchmark_latency()
    import torch
    device_name = "cuda" if torch.cuda.is_available() else "cpu"
    return MLBenchmarkResponse(
        intent_latency_ms=metrics["intent_latency_ms"],
        entity_latency_ms=metrics["entity_latency_ms"],
        total_latency_ms=metrics["total_latency_ms"],
        device=device_name,
        status="optimal",
    )
