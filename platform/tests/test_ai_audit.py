"""
AI Request Audit Tests

Covers the AIRequestLog model, the EventBus subscriber, the query functions,
and the GET /ai/usage endpoint.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from core.ai_audit import ai_usage_summary, list_ai_requests, persist_ai_request
from core.database import get_session
from core.main import app
from core.models_db import AIRequestLog
from fastapi.testclient import TestClient

client = TestClient(app)
client.headers.update({"X-API-Key": "test-api-key"})


# ---------------------------------------------------------------------------
# Model & persist_ai_request subscriber
# ---------------------------------------------------------------------------


def test_persist_ai_request_writes_success_record():
    persist_ai_request(
        {
            "provider": "anthropic",
            "status": "success",
            "duration_seconds": 1.5,
            "input_tokens": 200,
            "output_tokens": 100,
        }
    )
    session = get_session()
    try:
        logs = session.query(AIRequestLog).all()
        assert len(logs) == 1
        assert logs[0].provider == "anthropic"
        assert logs[0].status == "success"
        assert logs[0].duration_seconds == pytest.approx(1.5)
        assert logs[0].input_tokens == 200
        assert logs[0].output_tokens == 100
        assert logs[0].is_fallback is False
        assert logs[0].error is None
        assert logs[0].created_at is not None
    finally:
        session.close()


def test_persist_ai_request_writes_error_record():
    persist_ai_request(
        {
            "provider": "openai-compatible",
            "status": "error",
            "duration_seconds": 0.3,
            "error": "connection refused",
        }
    )
    session = get_session()
    try:
        log = session.query(AIRequestLog).one()
        assert log.status == "error"
        assert log.error == "connection refused"
        assert log.input_tokens is None
        assert log.output_tokens is None
    finally:
        session.close()


def test_persist_ai_request_writes_fallback_record():
    persist_ai_request(
        {
            "provider": "openai-compatible",
            "status": "success",
            "duration_seconds": 2.0,
            "input_tokens": 50,
            "output_tokens": 80,
            "is_fallback": True,
        }
    )
    session = get_session()
    try:
        log = session.query(AIRequestLog).one()
        assert log.is_fallback is True
    finally:
        session.close()


def test_persist_ai_request_handles_minimal_payload():
    persist_ai_request({})
    session = get_session()
    try:
        log = session.query(AIRequestLog).one()
        assert log.provider == "unknown"
        assert log.status == "unknown"
        assert log.duration_seconds is None
    finally:
        session.close()


def test_persist_ai_request_does_not_raise_on_db_error(monkeypatch):
    """Subscriber must not propagate exceptions to the caller."""
    import core.ai_audit

    monkeypatch.setattr(
        core.ai_audit, "get_session", lambda: (_ for _ in ()).throw(RuntimeError("db down"))
    )
    persist_ai_request({"provider": "test", "status": "success"})


# ---------------------------------------------------------------------------
# Query functions
# ---------------------------------------------------------------------------


def _seed_logs() -> None:
    """Insert a few log records for query tests."""
    session = get_session()
    try:
        now = datetime.now(UTC)
        records = [
            AIRequestLog(
                provider="anthropic",
                status="success",
                duration_seconds=1.0,
                input_tokens=100,
                output_tokens=50,
                is_fallback=False,
                created_at=now - timedelta(hours=2),
            ),
            AIRequestLog(
                provider="anthropic",
                status="error",
                duration_seconds=0.5,
                is_fallback=False,
                error="timeout",
                created_at=now - timedelta(hours=1),
            ),
            AIRequestLog(
                provider="openai-compatible",
                status="success",
                duration_seconds=2.0,
                input_tokens=200,
                output_tokens=80,
                is_fallback=True,
                created_at=now,
            ),
        ]
        session.add_all(records)
        session.commit()
    finally:
        session.close()


def test_list_ai_requests_returns_all():
    _seed_logs()
    session = get_session()
    try:
        logs = list_ai_requests(session)
        assert len(logs) == 3
    finally:
        session.close()


def test_list_ai_requests_orders_by_created_at_desc():
    _seed_logs()
    session = get_session()
    try:
        logs = list_ai_requests(session)
        assert logs[0].created_at >= logs[1].created_at >= logs[2].created_at
    finally:
        session.close()


def test_list_ai_requests_filters_by_provider():
    _seed_logs()
    session = get_session()
    try:
        logs = list_ai_requests(session, provider="openai-compatible")
        assert len(logs) == 1
        assert logs[0].provider == "openai-compatible"
    finally:
        session.close()


def test_list_ai_requests_filters_by_status():
    _seed_logs()
    session = get_session()
    try:
        logs = list_ai_requests(session, status="error")
        assert len(logs) == 1
        assert logs[0].status == "error"
    finally:
        session.close()


def test_list_ai_requests_filters_by_since():
    _seed_logs()
    session = get_session()
    try:
        since = datetime.now(UTC) - timedelta(minutes=30)
        logs = list_ai_requests(session, since=since)
        assert len(logs) == 1
        assert logs[0].provider == "openai-compatible"
    finally:
        session.close()


def test_list_ai_requests_pagination():
    _seed_logs()
    session = get_session()
    try:
        page1 = list_ai_requests(session, limit=2, offset=0)
        page2 = list_ai_requests(session, limit=2, offset=2)
        assert len(page1) == 2
        assert len(page2) == 1
    finally:
        session.close()


def test_ai_usage_summary_aggregates():
    _seed_logs()
    session = get_session()
    try:
        summary = ai_usage_summary(session)
        assert summary["total_requests"] == 3
        assert summary["total_input_tokens"] == 300
        assert summary["total_output_tokens"] == 130
    finally:
        session.close()


def test_ai_usage_summary_filters_by_provider():
    _seed_logs()
    session = get_session()
    try:
        summary = ai_usage_summary(session, provider="anthropic")
        assert summary["total_requests"] == 2
        assert summary["total_input_tokens"] == 100
        assert summary["total_output_tokens"] == 50
    finally:
        session.close()


def test_list_ai_requests_filters_by_until():
    _seed_logs()
    session = get_session()
    try:
        until = datetime.now(UTC) - timedelta(minutes=90)
        logs = list_ai_requests(session, until=until)
        assert len(logs) == 1
        assert logs[0].provider == "anthropic"
        assert logs[0].status == "success"
    finally:
        session.close()


def test_ai_usage_summary_filters_by_since():
    _seed_logs()
    session = get_session()
    try:
        since = datetime.now(UTC) - timedelta(minutes=30)
        summary = ai_usage_summary(session, since=since)
        assert summary["total_requests"] == 1
        assert summary["total_input_tokens"] == 200
    finally:
        session.close()


def test_ai_usage_summary_filters_by_until():
    _seed_logs()
    session = get_session()
    try:
        until = datetime.now(UTC) - timedelta(minutes=90)
        summary = ai_usage_summary(session, until=until)
        assert summary["total_requests"] == 1
        assert summary["total_input_tokens"] == 100
    finally:
        session.close()


def test_ai_usage_summary_empty_returns_zeros():
    session = get_session()
    try:
        summary = ai_usage_summary(session)
        assert summary["total_requests"] == 0
        assert summary["total_input_tokens"] == 0
        assert summary["total_output_tokens"] == 0
    finally:
        session.close()


# ---------------------------------------------------------------------------
# GET /ai/usage endpoint
# ---------------------------------------------------------------------------


def test_get_ai_usage_returns_empty():
    response = client.get("/ai/usage")
    assert response.status_code == 200
    body = response.json()
    assert body["total_requests"] == 0
    assert body["total_input_tokens"] == 0
    assert body["total_output_tokens"] == 0
    assert body["logs"] == []


def test_get_ai_usage_returns_seeded_data():
    _seed_logs()
    response = client.get("/ai/usage")
    assert response.status_code == 200
    body = response.json()
    assert body["total_requests"] == 3
    assert body["total_input_tokens"] == 300
    assert body["total_output_tokens"] == 130
    assert len(body["logs"]) == 3


def test_get_ai_usage_filters_by_provider():
    _seed_logs()
    response = client.get("/ai/usage", params={"provider": "anthropic"})
    assert response.status_code == 200
    body = response.json()
    assert body["total_requests"] == 2
    assert all(log["provider"] == "anthropic" for log in body["logs"])


def test_get_ai_usage_filters_by_status():
    _seed_logs()
    response = client.get("/ai/usage", params={"status": "error"})
    assert response.status_code == 200
    body = response.json()
    assert len(body["logs"]) == 1
    assert body["logs"][0]["status"] == "error"


def test_get_ai_usage_pagination():
    _seed_logs()
    response = client.get("/ai/usage", params={"limit": 1, "offset": 0})
    assert response.status_code == 200
    assert len(response.json()["logs"]) == 1


def test_get_ai_usage_requires_auth():
    no_auth_client = TestClient(app)
    response = no_auth_client.get("/ai/usage")
    assert response.status_code in (401, 403)
