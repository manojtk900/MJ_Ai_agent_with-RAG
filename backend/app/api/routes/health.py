"""
Health and Observability Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict


@router.get("/health", response_model=HealthResponse)
async def health_check():
    from app.config import settings
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        services={
            "api": "up",
            "database": "up",
            "redis": "up",
            "agents": "ready",
        },
    )


@router.get("/health/detailed")
async def detailed_health():
    """Detailed health check with DB and Redis connectivity."""
    from app.config import settings
    checks = {}

    # Check PostgreSQL
    try:
        from app.models.base import engine
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        checks["postgresql"] = {"status": "up"}
    except Exception as e:
        checks["postgresql"] = {"status": "down", "error": str(e)}

    # Check Redis
    try:
        from app.core.memory.short_term import redis_memory
        await redis_memory.set("health_check", "ok", ttl=5)
        checks["redis"] = {"status": "up"}
    except Exception as e:
        checks["redis"] = {"status": "down", "error": str(e)}

    overall = "healthy" if all(v.get("status") == "up" for v in checks.values()) else "degraded"
    return {"status": overall, "version": settings.app_version, "checks": checks}


@router.get("/api/v1/health/llm")
@router.get("/health/llm")
async def llm_health():
    """LLM provider health check endpoint."""
    from app.config import settings
    import httpx

    status_str = "connected"
    if settings.default_llm_provider == "ollama":
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{settings.ollama_base_url}/api/tags")
                if resp.status_code != 200:
                    status_str = "degraded"
        except Exception:
            status_str = "disconnected"

    return {
        "provider": settings.default_llm_provider,
        "model": settings.ollama_default_model if settings.default_llm_provider == "ollama" else settings.openai_default_model,
        "status": status_str,
    }
