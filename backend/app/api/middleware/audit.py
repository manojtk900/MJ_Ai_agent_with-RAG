"""
Audit Middleware — Logs every request with method, path, status, latency.
"""
import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

log = structlog.get_logger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Logs every HTTP request for the audit trail.
    Captures: method, path, status_code, latency_ms, client_ip.
    """

    SKIP_PATHS = {"/health", "/metrics", "/docs", "/redoc", "/openapi.json", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip noisy paths
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        request_id = str(uuid.uuid4())[:8]
        start_time = time.monotonic()

        # Attach request_id to headers for tracing
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            latency_ms = round((time.monotonic() - start_time) * 1000, 2)

            log.info(
                "HTTP request",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                latency_ms=latency_ms,
                client=request.client.host if request.client else "unknown",
            )

            # Add request ID to response headers for client-side correlation
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as exc:
            latency_ms = round((time.monotonic() - start_time) * 1000, 2)
            log.error(
                "HTTP request failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                error=str(exc),
                latency_ms=latency_ms,
            )
            raise
