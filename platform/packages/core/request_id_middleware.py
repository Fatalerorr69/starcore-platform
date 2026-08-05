"""
Request ID Middleware for FastAPI

Provides request correlation via X-Request-ID header.
"""

from __future__ import annotations

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .correlation import contextualize_request, resolve_request_id


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware that binds X-Request-ID to all requests.

    - Accepts caller-supplied X-Request-ID header
    - Falls back to generating new UUID if missing or invalid
    - Binds to asyncio context for automatic propagation
    - Returns X-Request-ID in response header
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Resolve request ID from header or generate new one
        incoming = request.headers.get("x-request-id")
        request_id = resolve_request_id(incoming)

        # Contextualize the async context with this request ID
        contextualize_request(request_id)

        # Call the actual request handler
        response = await call_next(request)

        # Echo request ID back in response
        response.headers["X-Request-ID"] = request_id

        return response
