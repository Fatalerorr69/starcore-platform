"""
WebSocket blueprint execution endpoint tests — WS /blueprints/run/ws.

Verifies authentication (JWT / legacy API key), role enforcement, event
streaming, disconnect-cancel semantics, and error paths.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Generator
from typing import Any
from unittest.mock import patch

import jwt
import pytest
from blueprints.models import Blueprint, ResourceSpec
from blueprints.template_resolver import TemplateResolutionError
from core.config import get_settings
from core.main import app
from core.routers.ws import _ws_run_blueprint
from fastapi.testclient import TestClient
from provider_sdk.base import BaseProvider
from provider_sdk.registry import registry
from starlette.websockets import WebSocketDisconnect

_JWT_SECRET = "test-ws-jwt-secret-at-least-32-bytes!"
_ALGORITHM = "HS256"

client = TestClient(app)


# ── Fake providers ─────────────────────────────────────────────────────────────


class _FakeProvider(BaseProvider):
    name = "fake-ws"

    def __init__(self) -> None:
        self.executed: list[str] = []

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> None:
        pass

    async def health(self) -> dict[str, Any]:
        return {"status": "ok"}

    async def list_resources(self) -> list[dict[str, Any]]:
        return []

    async def execute(self, task) -> None:
        self.executed.append(task.resource)


@pytest.fixture
def fake_provider() -> Generator[_FakeProvider, None, None]:
    p = _FakeProvider()
    registry.register(p)
    yield p
    registry._providers.clear()


# ── Helpers ────────────────────────────────────────────────────────────────────


def _bp(*resource_names: str, name: str = "test-bp") -> str:
    return json.dumps(
        {
            "name": name,
            "version": "1.0",
            "resources": [
                {"name": r, "provider": "fake-ws", "kind": "svc", "config": {}}
                for r in resource_names
            ],
        }
    )


def _make_token(role: str, *, expired: bool = False) -> str:
    from datetime import UTC, datetime, timedelta

    exp = datetime.now(UTC) + (timedelta(seconds=-1) if expired else timedelta(minutes=30))
    payload = {
        "sub": "testuser",
        "role": role,
        "type": "access",
        "exp": exp,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm=_ALGORITHM)


def _collect_ws_events(url: str) -> tuple[list[dict], int | None]:
    """Connect, send blueprint, collect all events until disconnect.

    Returns (events, close_code).  close_code is None when the server closed
    with the normal handshake (code 1000 is swallowed by the context manager).
    """
    events: list[dict] = []
    try:
        with client.websocket_connect(url) as ws:
            ws.send_text(_bp("r1"))
            try:
                while True:
                    events.append(ws.receive_json())
            except WebSocketDisconnect:
                pass
    except WebSocketDisconnect:
        pass
    return events, None


# ── Authentication ─────────────────────────────────────────────────────────────


def test_ws_no_auth_rejects():
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/blueprints/run/ws") as ws:
            ws.receive_text()
    assert exc_info.value.code == 4401


def test_ws_wrong_api_key_rejects():
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/blueprints/run/ws?api_key=wrong-key") as ws:
            ws.receive_text()
    assert exc_info.value.code == 4401


def test_ws_api_key_not_configured_on_server(monkeypatch):
    monkeypatch.delenv("STARCORE_API_KEY")
    get_settings.cache_clear()
    try:
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect("/blueprints/run/ws?api_key=any") as ws:
                ws.receive_text()
        assert exc_info.value.code == 4401
    finally:
        get_settings.cache_clear()


def test_ws_expired_token_rejects(monkeypatch):
    monkeypatch.setenv("STARCORE_JWT_SECRET_KEY", _JWT_SECRET)
    get_settings.cache_clear()
    try:
        tok = _make_token("operator", expired=True)
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(f"/blueprints/run/ws?token={tok}") as ws:
                ws.receive_text()
        assert exc_info.value.code == 4401
    finally:
        get_settings.cache_clear()


def test_ws_invalid_token_rejects(monkeypatch):
    monkeypatch.setenv("STARCORE_JWT_SECRET_KEY", _JWT_SECRET)
    get_settings.cache_clear()
    try:
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect("/blueprints/run/ws?token=garbage") as ws:
                ws.receive_text()
        assert exc_info.value.code == 4401
    finally:
        get_settings.cache_clear()


def test_ws_jwt_not_configured_returns_4403(monkeypatch):
    """When JWT_SECRET_KEY is absent on the server, token auth → 4403."""
    monkeypatch.delenv("STARCORE_JWT_SECRET_KEY", raising=False)
    get_settings.cache_clear()
    try:
        tok = jwt.encode(
            {"sub": "x", "role": "operator", "type": "access"},
            "any-secret",
            algorithm="HS256",
        )
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(f"/blueprints/run/ws?token={tok}") as ws:
                ws.receive_text()
        assert exc_info.value.code == 4403
    finally:
        get_settings.cache_clear()


def test_ws_token_with_invalid_role_rejects(monkeypatch):
    """A JWT signed correctly but with an unrecognised role → 4401."""
    monkeypatch.setenv("STARCORE_JWT_SECRET_KEY", _JWT_SECRET)
    get_settings.cache_clear()
    try:
        from datetime import UTC, datetime, timedelta

        payload = {
            "sub": "x",
            "role": "superadmin",
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=30),
            "iat": datetime.now(UTC),
        }
        tok = jwt.encode(payload, _JWT_SECRET, algorithm=_ALGORITHM)
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(f"/blueprints/run/ws?token={tok}") as ws:
                ws.receive_text()
        assert exc_info.value.code == 4401
    finally:
        get_settings.cache_clear()


def test_ws_reader_role_rejects(monkeypatch):
    """reader role is below the operator minimum — must close 4403."""
    monkeypatch.setenv("STARCORE_JWT_SECRET_KEY", _JWT_SECRET)
    get_settings.cache_clear()
    try:
        tok = _make_token("reader")
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(f"/blueprints/run/ws?token={tok}") as ws:
                ws.receive_text()
        assert exc_info.value.code == 4403
    finally:
        get_settings.cache_clear()


# ── Happy-path execution ───────────────────────────────────────────────────────


def test_ws_valid_api_key_streams_all_events(fake_provider):
    events, _ = _collect_ws_events("/blueprints/run/ws?api_key=test-api-key")
    names = [e["event"] for e in events]
    assert "task.started" in names
    assert "task.completed" in names
    assert "run.completed" in names
    assert "run.persisted" in names
    assert names[-1] == "run.persisted"


def test_ws_valid_bearer_token_streams_events(fake_provider, monkeypatch):
    monkeypatch.setenv("STARCORE_JWT_SECRET_KEY", _JWT_SECRET)
    get_settings.cache_clear()
    try:
        tok = _make_token("operator")
        events, _ = _collect_ws_events(f"/blueprints/run/ws?token={tok}")
        assert any(e["event"] == "run.persisted" for e in events)
    finally:
        get_settings.cache_clear()


def test_ws_run_persisted_has_run_id(fake_provider):
    events, _ = _collect_ws_events("/blueprints/run/ws?api_key=test-api-key")
    persisted = next(e for e in events if e["event"] == "run.persisted")
    assert persisted["run_id"]


def test_ws_events_in_order(fake_provider):
    events, _ = _collect_ws_events("/blueprints/run/ws?api_key=test-api-key")
    names = [e["event"] for e in events]
    assert names.index("task.started") < names.index("task.completed")
    assert names.index("task.completed") < names.index("run.completed")
    assert names.index("run.completed") < names.index("run.persisted")


def test_ws_run_completed_has_blueprint_name(fake_provider):
    events, _ = _collect_ws_events("/blueprints/run/ws?api_key=test-api-key")
    evt = next(e for e in events if e["event"] == "run.completed")
    assert evt["blueprint_name"] == "test-bp"


def test_ws_task_completed_has_status(fake_provider):
    events, _ = _collect_ws_events("/blueprints/run/ws?api_key=test-api-key")
    completed = [e for e in events if e["event"] == "task.completed"]
    assert all("status" in e for e in completed)


def test_ws_multiple_resources_all_complete(fake_provider):
    events, _ = _collect_ws_events("/blueprints/run/ws?api_key=test-api-key")
    with client.websocket_connect("/blueprints/run/ws?api_key=test-api-key") as ws:
        ws.send_text(_bp("a", "b", "c"))
        evts: list[dict] = []
        try:
            while True:
                evts.append(ws.receive_json())
        except WebSocketDisconnect:
            pass
    assert sum(1 for e in evts if e["event"] == "task.started") == 3
    assert sum(1 for e in evts if e["event"] == "task.completed") == 3


def test_ws_parallel_execution(fake_provider):
    events, _ = _collect_ws_events("/blueprints/run/ws?api_key=test-api-key&parallel=true")
    names = [e["event"] for e in events]
    assert "run.completed" in names
    assert "run.persisted" in names


# ── Error paths ────────────────────────────────────────────────────────────────


def test_ws_invalid_blueprint_json_sends_error_event():
    with client.websocket_connect("/blueprints/run/ws?api_key=test-api-key") as ws:
        ws.send_text("this is not valid json {{{")
        evt = ws.receive_json()
        assert evt["event"] == "error"
        assert "detail" in evt
        with pytest.raises(WebSocketDisconnect) as exc_info:
            ws.receive_json()
    assert exc_info.value.code == 4422


def test_ws_template_resolution_error_sends_error_event():
    with patch(
        "core.routers.ws.resolve_templates",
        side_effect=TemplateResolutionError("bad template"),
    ):
        with client.websocket_connect("/blueprints/run/ws?api_key=test-api-key") as ws:
            ws.send_text(_bp("r"))
            evt = ws.receive_json()
            assert evt["event"] == "error"
            assert "bad template" in evt["detail"]
            with pytest.raises(WebSocketDisconnect) as exc_info:
                ws.receive_json()
        assert exc_info.value.code == 4422


# ── Disconnect / cancel semantics ─────────────────────────────────────────────


def test_ws_disconnect_before_sending_blueprint():
    """Server handles client closing before sending blueprint without crashing."""
    with client.websocket_connect("/blueprints/run/ws?api_key=test-api-key"):
        pass  # close immediately without sending blueprint


@pytest.mark.anyio
async def test_ws_run_blueprint_disconnect_cancels_exec_task():
    """WebSocketDisconnect during streaming triggers exec_task cancellation."""
    blocker: asyncio.Event = asyncio.Event()

    class _SlowProvider(BaseProvider):
        name = "slow-ws-cancel-test"

        async def connect(self) -> bool:
            return True

        async def disconnect(self) -> None:
            pass

        async def health(self) -> dict[str, Any]:
            return {}

        async def list_resources(self) -> list[dict[str, Any]]:
            return []

        async def execute(self, task) -> None:
            await blocker.wait()

    registry._providers.clear()
    registry.register(_SlowProvider())
    try:
        bp = Blueprint(
            name="ws-cancel-test",
            version="1.0",
            resources=[
                ResourceSpec(name="r", provider="slow-ws-cancel-test", kind="svc", config={})
            ],
        )

        class _MockWS:
            async def receive_text(self) -> str:
                return bp.model_dump_json()

            async def send_text(self, data: str) -> None:
                raise WebSocketDisconnect(code=1001, reason="client gone")

            async def close(self, code: int = 1000, reason: str = "") -> None:
                pass

        await _ws_run_blueprint(_MockWS(), False)  # type: ignore[arg-type]
    finally:
        blocker.set()
        registry._providers.clear()
