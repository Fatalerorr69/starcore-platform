"""
AI Request Audit — persists ai.request.completed events to the database.

Subscribes to the EventBus at import time (like metrics.py). The subscriber
writes an AIRequestLog row for every AI generation request, enabling the
GET /ai/usage endpoint to report historical usage and cost data.
"""

from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from core.database import get_session
from core.events import event_bus
from core.models_db import AIRequestLog

logger = logging.getLogger(__name__)


def persist_ai_request(payload: dict) -> None:
    """EventBus subscriber for "ai.request.completed"."""
    try:
        session = get_session()
        try:
            log = AIRequestLog(
                provider=payload.get("provider", "unknown"),
                status=payload.get("status", "unknown"),
                duration_seconds=payload.get("duration_seconds"),
                input_tokens=payload.get("input_tokens"),
                output_tokens=payload.get("output_tokens"),
                is_fallback=bool(payload.get("is_fallback", False)),
                error=payload.get("error"),
            )
            session.add(log)
            session.commit()
        finally:
            session.close()
    except Exception:
        logger.warning("Failed to persist AI request log", exc_info=True)


event_bus.subscribe("ai.request.completed", persist_ai_request)


def list_ai_requests(
    session: Session,
    *,
    limit: int = 50,
    offset: int = 0,
    provider: str | None = None,
    status: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
) -> list[AIRequestLog]:
    query = session.query(AIRequestLog).order_by(AIRequestLog.created_at.desc())
    if provider is not None:
        query = query.filter(AIRequestLog.provider == provider)
    if status is not None:
        query = query.filter(AIRequestLog.status == status)
    if since is not None:
        query = query.filter(AIRequestLog.created_at >= since)
    if until is not None:
        query = query.filter(AIRequestLog.created_at <= until)
    if offset:
        query = query.offset(offset)
    return query.limit(limit).all()


def ai_usage_summary(
    session: Session,
    *,
    provider: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
) -> dict:
    """Aggregate token counts and request totals."""
    query = session.query(
        func.count(AIRequestLog.id).label("total_requests"),
        func.coalesce(func.sum(AIRequestLog.input_tokens), 0).label("total_input_tokens"),
        func.coalesce(func.sum(AIRequestLog.output_tokens), 0).label("total_output_tokens"),
    )
    if provider is not None:
        query = query.filter(AIRequestLog.provider == provider)
    if since is not None:
        query = query.filter(AIRequestLog.created_at >= since)
    if until is not None:
        query = query.filter(AIRequestLog.created_at <= until)
    row = query.one()
    return {
        "total_requests": row.total_requests,
        "total_input_tokens": row.total_input_tokens,
        "total_output_tokens": row.total_output_tokens,
    }
