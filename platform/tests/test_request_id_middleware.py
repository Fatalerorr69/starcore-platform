"""Tests for core.request_id_middleware — RequestIdMiddleware."""

from __future__ import annotations

import re

from core.request_id_middleware import RequestIdMiddleware
from fastapi import FastAPI
from fastapi.testclient import TestClient

_UUID4 = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


def _make_client() -> TestClient:
    app = FastAPI()
    app.add_middleware(RequestIdMiddleware)

    @app.get("/ping")
    def ping():
        return {"ok": True}

    return TestClient(app)


def test_middleware_echoes_valid_request_id():
    client = _make_client()
    resp = client.get("/ping", headers={"X-Request-ID": "valid-id-abc"})
    assert resp.headers["x-request-id"] == "valid-id-abc"


def test_middleware_generates_uuid4_when_no_header():
    client = _make_client()
    resp = client.get("/ping")
    assert _UUID4.match(resp.headers["x-request-id"])


def test_middleware_generates_uuid4_for_invalid_header():
    client = _make_client()
    resp = client.get("/ping", headers={"X-Request-ID": "bad id with spaces!"})
    assert _UUID4.match(resp.headers["x-request-id"])
