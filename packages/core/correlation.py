"""
Request Correlation & Context Propagation

Provides request ID correlation across async tasks for improved observability:
- Generate or accept caller-supplied X-Request-ID
- Propagate through asyncio context
- Available to all loggers and diagnostics
"""

from __future__ import annotations

import contextvars
import re
import uuid
from typing import Optional

from loguru import logger

# ContextVar for request ID propagation
_request_id_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)

# Validation pattern for request IDs
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def set_request_id(request_id: str | None) -> None:
    """Set the current request ID for this context.
    
    Args:
        request_id: Request ID (must match pattern or be None).
    
    Raises:
        ValueError: If request_id doesn't match pattern.
    """
    if request_id is not None and not _REQUEST_ID_PATTERN.fullmatch(request_id):
        raise ValueError(
            f"Request ID must match pattern {_REQUEST_ID_PATTERN.pattern}, got: {request_id}"
        )
    _request_id_context.set(request_id)


def get_request_id() -> str | None:
    """Get the current request ID.
    
    Returns:
        Current request ID or None if not set.
    """
    return _request_id_context.get()


def resolve_request_id(incoming: str | None) -> str:
    """Resolve a request ID from incoming header or generate new one.
    
    Accepts caller-supplied X-Request-ID if it looks like a reasonable opaque token,
    otherwise generates a new one. A malformed or missing header is not an error.
    
    Args:
        incoming: Request ID from X-Request-ID header (or None).
    
    Returns:
        Valid request ID (either incoming or newly generated).
    """
    if incoming and _REQUEST_ID_PATTERN.fullmatch(incoming):
        return incoming
    return str(uuid.uuid4())


def contextualize_request(request_id: str) -> None:
    """Contextualize the current async context with request ID.
    
    This binds the request ID to the current asyncio context, making it
    automatically available to all log entries emitted from this context
    and any child coroutines.
    
    Args:
        request_id: Request ID to bind.
    """
    set_request_id(request_id)
    logger.contextualize(request_id=request_id)
