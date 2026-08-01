"""
Request Correlation ID Tests
"""

from __future__ import annotations

import asyncio
import re
from unittest.mock import patch

from core.main import _REQUEST_ID_PATTERN, _resolve_request_id, app
from fastapi.testclient import TestClient
from loguru import logger
from provider_sdk.base import BaseProvider
from provider_sdk.registry import registry

client = TestClient(app)
client.headers.update({"X-API-Key": "test-api-key"})

_UUID4 = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


# ---------------------------------------------------------------------------
# _resolve_request_id unit tests
# ---------------------------------------------------------------------------


def test_resolve_request_id_generates_when_missing():
    result = _resolve_request_id(None)
    assert _UUID4.match(result)


def test_resolve_request_id_generates_when_empty():
    result = _resolve_request_id("")
    assert _UUID4.match(result)


def test_resolve_request_id_accepts_valid_supplied_id():
    assert _resolve_request_id("my-trace-id-123") == "my-trace-id-123"


def test_resolve_request_id_rejects_id_with_whitespace():
    result = _resolve_request_id("bad id with spaces")
    assert _UUID4.match(result)


def test_resolve_request_id_rejects_id_with_newline():
    result = _resolve_request_id("bad-id\nwith-newline")
    assert _UUID4.match(result)


def test_resolve_request_id_rejects_id_over_128_chars():
    result = _resolve_request_id("a" * 129)
    assert _UUID4.match(result)


def test_resolve_request_id_accepts_id_at_128_char_boundary():
    candidate = "a" * 128
    assert _resolve_request_id(candidate) == candidate


def test_request_id_pattern_allows_alnum_hyphen_underscore():
    assert _REQUEST_ID_PATTERN.fullmatch("abc-DEF_123")


# ---------------------------------------------------------------------------
# Middleware / response header
# ---------------------------------------------------------------------------


def test_response_includes_generated_request_id_header():
    response = client.get("/health")
    assert _UUID4.match(response.headers["x-request-id"])


def test_response_echoes_supplied_valid_request_id():
    response = client.get("/health", headers={"X-Request-ID": "caller-supplied-trace"})
    assert response.headers["x-request-id"] == "caller-supplied-trace"


def test_response_replaces_invalid_supplied_request_id():
    response = client.get("/health", headers={"X-Request-ID": "not a valid id!"})
    assert response.headers["x-request-id"] != "not a valid id!"
    assert _UUID4.match(response.headers["x-request-id"])


def test_sequential_requests_without_supplied_id_get_different_ids():
    r1 = client.get("/health")
    r2 = client.get("/health")
    assert r1.headers["x-request-id"] != r2.headers["x-request-id"]


# ---------------------------------------------------------------------------
# Logging context propagation
# ---------------------------------------------------------------------------


def test_request_id_is_bound_to_log_records_during_the_request():
    captured = []
    sink_id = logger.add(lambda message: captured.append(message.record), level="WARNING")
    try:
        payload = {
            "name": "req-id-log-test",
            "version": "1.0",
            "resources": [{"name": "thing", "provider": "ghost", "kind": "svc", "config": {}}],
        }
        response = client.post(
            "/blueprints/run", json=payload, headers={"X-Request-ID": "log-trace-42"}
        )
        assert response.status_code == 200
    finally:
        logger.remove(sink_id)

    matching = [r for r in captured if r["extra"].get("request_id") == "log-trace-42"]
    assert matching, "expected at least one log record bound to this request's ID"


def test_request_id_reverts_to_default_outside_request_context():
    captured = []
    sink_id = logger.add(lambda message: captured.append(message.record), level="INFO")
    try:
        logger.info("outside any request")
    finally:
        logger.remove(sink_id)

    assert captured[-1]["extra"]["request_id"] == "-"


# ---------------------------------------------------------------------------
# Context propagation through asyncio.to_thread
# ---------------------------------------------------------------------------


async def test_loguru_context_propagates_through_asyncio_to_thread():
    """loguru.contextualize() binds via contextvars, which asyncio.to_thread()
    copies into the spawned thread (Python 3.10+). Verify the propagation in
    isolation, with no HTTP layer involved."""
    captured: list = []
    sink_id = logger.add(lambda message: captured.append(message.record), level="INFO")
    try:
        with logger.contextualize(request_id="thread-ctx-42"):
            await asyncio.to_thread(lambda: logger.info("message from thread"))
    finally:
        logger.remove(sink_id)

    assert len(captured) == 1
    assert captured[0]["extra"]["request_id"] == "thread-ctx-42"


def test_request_id_propagates_to_provider_execute_log():
    """End-to-end: X-Request-ID from the HTTP layer must reach logger.info()
    calls inside provider.execute(), both in the async coroutine and in any
    asyncio.to_thread() call the provider makes."""

    class _LoggingProvider(BaseProvider):
        name = "logging-test-provider"

        async def connect(self) -> bool:
            return True

        async def disconnect(self) -> None:
            return None

        async def health(self) -> dict:
            return {"status": "ok"}

        async def list_resources(self) -> list:
            return []

        async def execute(self, task) -> None:
            logger.info("[LoggingProvider] async-execute")
            await asyncio.to_thread(lambda: logger.info("[LoggingProvider] thread-execute"))

    captured: list = []
    sink_id = logger.add(lambda message: captured.append(message.record), level="INFO")

    saved = dict(registry._providers)
    registry._providers["logging-test-provider"] = _LoggingProvider()
    try:
        payload = {
            "name": "corr-id-provider-test",
            "version": "1.0",
            "resources": [
                {
                    "name": "thing",
                    "provider": "logging-test-provider",
                    "kind": "svc",
                    "config": {},
                }
            ],
        }
        with patch("blueprints.executor.register_default_providers"):
            response = client.post(
                "/blueprints/run",
                json=payload,
                headers={"X-Request-ID": "provider-trace-id"},
            )
        assert response.status_code == 200
    finally:
        logger.remove(sink_id)
        registry._providers.clear()
        registry._providers.update(saved)

    provider_logs = [r for r in captured if "[LoggingProvider]" in r["message"]]
    assert len(provider_logs) == 2, (
        f"expected 2 provider log records, got {len(provider_logs)}: "
        f"{[r['message'] for r in captured]}"
    )
    for record in provider_logs:
        assert record["extra"]["request_id"] == "provider-trace-id", (
            f"expected 'provider-trace-id', got {record['extra']['request_id']!r}"
        )
