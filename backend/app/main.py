"""
MJ AI Assistant — FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.api.routes import chat, agents, memory, voice, tasks, health, projects, tools, auth, notifications, ml, intelligence
from app.api.middleware.audit import AuditMiddleware

from app.core.observability.tracing import setup_tracing

# ── Structured Logging Setup ──────────────────────────────────
# structlog v26 API — use contextvars for async support
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.ExceptionRenderer(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan — startup and shutdown events."""
    # ── Startup ───────────────────────────────────────────────
    log.info("🚀 MJ AI Assistant starting up...", version=settings.app_version)
    log.info(f"Provider: {settings.default_llm_provider}")
    log.info(f"Model: {settings.ollama_default_model}")
    print(f"Provider: {settings.default_llm_provider}")
    print(f"Model: {settings.ollama_default_model}")

    # Setup OpenTelemetry tracing (only in production)
    if not settings.debug:
        try:
            setup_tracing()
        except Exception as e:
            log.warning("Tracing setup skipped", error=str(e))

    # Pre-load local ML models (Intent Classifier & NER)
    try:
        from app.agents.ml_router import load_models
        load_models()
        log.info("✅ ML Models loaded into memory (Intent + Entity)")
    except Exception as e:
        log.warning("⚠️  ML Model loading failed", error=str(e))

    # Create database tables (graceful — won't crash if DB is unavailable)
    try:
        from app.models.base import create_tables
        await create_tables()
        log.info("✅ Database tables ready")
    except Exception as e:
        log.warning(
            "⚠️  Database not available — running without persistence",
            error=str(e),
            hint="Start PostgreSQL: docker compose up -d postgres",
        )

    # Initialize Redis connection pool (graceful)
    try:
        from app.core.memory.short_term import RedisMemory
        app.state.redis = await RedisMemory.create_pool(settings.redis_url)
        log.info("✅ Redis connected")
    except Exception as e:
        app.state.redis = None
        log.warning(
            "⚠️  Redis not available — running without session cache",
            error=str(e),
            hint="Start Redis: docker compose up -d redis",
        )

    # Initialize APScheduler TaskScheduler
    try:
        from app.services.scheduler import scheduler_service
        scheduler_service.start()
    except Exception as e:
        log.warning("⚠️ TaskScheduler start failed", error=str(e))

    log.info("✅ MJ AI Assistant ready", env=settings.app_env, debug=settings.debug)

    yield

    # ── Shutdown ──────────────────────────────────────────────
    log.info("🛑 MJ AI Assistant shutting down...")
    try:
        from app.services.scheduler import scheduler_service
        scheduler_service.shutdown()
    except Exception:
        pass

    if hasattr(app.state, "redis") and app.state.redis is not None:
        try:
            await app.state.redis.aclose()
        except Exception:
            pass

    log.info("👋 Shutdown complete")


# ── FastAPI App Factory ───────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Production-grade AI Agent Operating System",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ── Middleware (order matters: outer → inner) ─────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(AuditMiddleware)

    # ── Prometheus Metrics ────────────────────────────────────
    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        excluded_handlers=["/health", "/metrics"],
    ).instrument(app).expose(app, include_in_schema=False, tags=["observability"])

    # ── Root Redirect / Info Endpoint ─────────────────────────
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint — returns system metadata and docs link."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "online",
            "docs_url": "/docs",
            "health_url": "/health",
            "api_v1_prefix": settings.api_v1_prefix,
        }

    # ── Routers ───────────────────────────────────────────────
    prefix = settings.api_v1_prefix
    app.include_router(health.router, tags=["health"])
    app.include_router(chat.router, prefix=prefix, tags=["chat"])
    app.include_router(intelligence.router, prefix=prefix, tags=["intelligence"])
    app.include_router(agents.router, prefix=prefix, tags=["agents"])
    app.include_router(ml.router, prefix=prefix, tags=["ml"])
    app.include_router(memory.router, prefix=prefix, tags=["memory"])
    app.include_router(voice.router, prefix=prefix, tags=["voice"])
    app.include_router(tasks.router, prefix=prefix, tags=["tasks"])
    app.include_router(projects.router, prefix=prefix, tags=["projects"])
    app.include_router(tools.router, prefix=prefix, tags=["tools"])
    app.include_router(auth.router, prefix=prefix, tags=["auth"])
    app.include_router(notifications.router, prefix=prefix, tags=["notifications"])


    # ── Global Exception Handlers ─────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        log.error("Unhandled exception", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
                "path": str(request.url.path),
            },
        )

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
