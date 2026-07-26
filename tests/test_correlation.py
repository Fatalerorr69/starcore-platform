"""Tests for core.correlation — set/get_request_id, resolve_request_id, contextualize_request."""

from __future__ import annotations

import re
import uuid

import pytest
from core.correlation import (
    contextualize_request,
    get_request_id,
    resolve_request_id,
    set_request_id,
)

_UUID4 = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


# ── set_request_id / get_request_id ──────────────────────────────────────────


def test_set_and_get_request_id():
    set_request_id("my-request-abc")
    assert get_request_id() == "my-request-abc"


def test_set_request_id_clears_with_none():
    set_request_id("initial")
    set_request_id(None)
    assert get_request_id() is None


def test_set_request_id_invalid_raises_value_error():
    with pytest.raises(ValueError, match="Request ID must match pattern"):
        set_request_id("invalid id with spaces")


def test_set_request_id_too_long_raises_value_error():
    with pytest.raises(ValueError):
        set_request_id("a" * 129)


# ── resolve_request_id ───────────────────────────────────────────────────────


def test_resolve_request_id_echoes_valid_token():
    result = resolve_request_id("valid-id-123")
    assert result == "valid-id-123"


def test_resolve_request_id_none_generates_uuid4():
    result = resolve_request_id(None)
    parsed = uuid.UUID(result)
    assert parsed.version == 4
    assert _UUID4.match(result)


def test_resolve_request_id_invalid_generates_uuid4():
    result = resolve_request_id("bad id!")
    assert _UUID4.match(result)


def test_resolve_request_id_empty_generates_uuid4():
    result = resolve_request_id("")
    assert _UUID4.match(result)


# ── contextualize_request ────────────────────────────────────────────────────


def test_contextualize_request_sets_request_id():
    contextualize_request("ctx-id-789")
    assert get_request_id() == "ctx-id-789"
