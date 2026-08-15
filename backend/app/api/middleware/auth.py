"""
Auth Middleware — JWT token validation (stub for development).
Full implementation: extract Bearer token, validate JWT, attach user to request.state.
"""
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    """
    JWT Authentication middleware.
    In development mode (DEBUG=true), all requests pass through.
    In production, validates Bearer tokens.
    """

    # Paths that are always public (no auth required)
    PUBLIC_PATHS = {
        "/health",
        "/health/detailed",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Always allow public paths
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)

        from app.config import settings

        # In debug mode, skip auth entirely (development convenience)
        if settings.debug:
            request.state.user_id = None
            request.state.user_role = "admin"
            return await call_next(request)

        # Production: extract and validate JWT
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401,
                content={"error": "unauthorized", "message": "Bearer token required"},
            )

        token = auth_header[7:]
        try:
            from jose import jwt, JWTError
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            request.state.user_id = payload.get("sub")
            request.state.user_role = payload.get("role", "user")
        except Exception:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401,
                content={"error": "invalid_token", "message": "Token is invalid or expired"},
            )

        return await call_next(request)
