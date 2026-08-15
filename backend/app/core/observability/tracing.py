"""
Observability — OpenTelemetry setup with LangSmith integration.
"""
from __future__ import annotations
import structlog
from app.config import settings

log = structlog.get_logger(__name__)


def setup_tracing() -> None:
    """Configure OpenTelemetry tracing for production."""
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        provider = TracerProvider()
        exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor().instrument()

        log.info("OpenTelemetry tracing initialized", endpoint=settings.otel_exporter_otlp_endpoint)
    except ImportError:
        log.warning("OpenTelemetry not installed — skipping tracing setup")
    except Exception as e:
        log.error("Tracing setup failed", error=str(e))


def setup_langsmith() -> None:
    """Configure LangSmith for LangGraph workflow tracing."""
    import os
    if settings.langchain_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
        log.info("LangSmith tracing enabled", project=settings.langchain_project)


def get_tracer(name: str):
    """Get a named tracer for manual instrumentation."""
    try:
        from opentelemetry import trace
        return trace.get_tracer(name)
    except Exception:
        return None
