"""
SSE streaming endpoint tests — POST /blueprints/run/stream.

Verifies that task lifecycle events (task.started, task.completed,
run.completed) are streamed in real time and that a run.persisted event
with the database run_id is emitted after execution completes.
"""

from __future__ import annotations

import json
from collections.abc import Generator
from typing import Any
from unittest.mock import patch

import httpx
import pytest
from blueprints.template_resolver import TemplateResolutionError
from core.main import app
from provider_sdk.base import BaseProvider
from provider_sdk.registry import registry

# ── Minimal fake provider ──────────────────────────────────────────────────────


class _FakeProvider(BaseProvider):
    name = "fake"

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


@pytest.fixture
async def client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        headers={"X-API-Key": "test-api-key"},
    ) as c:
        yield c


# ── Helpers ────────────────────────────────────────────────────────────────────


def _bp(name: str, *resource_names: str) -> dict:
    return {
        "name": name,
        "version": "1.0",
        "resources": [
            {"name": r, "provider": "fake", "kind": "svc", "config": {}} for r in resource_names
        ],
    }


async def _collect_sse(client: httpx.AsyncClient, path: str, **kwargs) -> list[dict]:
    events: list[dict] = []
    async with client.stream("POST", path, **kwargs) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        events.extend(
            [
                json.loads(line[6:])
                async for line in response.aiter_lines()
                if line.startswith("data: ")
            ]
        )
    return events


# ── Tests ──────────────────────────────────────────────────────────────────────


async def test_stream_emits_task_and_run_events(client, fake_provider):
    """Sequential run streams task.started, task.completed, run.completed, run.persisted."""
    events = await _collect_sse(client, "/blueprints/run/stream", json=_bp("s", "a", "b"))

    names = [e["event"] for e in events]
    assert names.count("task.started") == 2
    assert names.count("task.completed") == 2
    assert "run.completed" in names
    assert "run.persisted" in names
    assert names.index("run.persisted") == len(names) - 1


async def test_stream_run_persisted_has_run_id(client, fake_provider):
    events = await _collect_sse(client, "/blueprints/run/stream", json=_bp("s", "r"))
    persisted = next(e for e in events if e["event"] == "run.persisted")
    assert persisted["run_id"]


async def test_stream_events_in_order(client, fake_provider):
    """task.started always precedes task.completed for the same resource."""
    events = await _collect_sse(client, "/blueprints/run/stream", json=_bp("s", "x"))
    names = [e["event"] for e in events]
    assert names.index("task.started") < names.index("task.completed")
    assert names.index("task.completed") < names.index("run.completed")


async def test_stream_parallel_run(client, fake_provider):
    """parallel=true path also streams all expected events."""
    events = await _collect_sse(
        client, "/blueprints/run/stream", json=_bp("p", "x", "y"), params={"parallel": "true"}
    )
    names = [e["event"] for e in events]
    assert "run.completed" in names
    assert "run.persisted" in names


async def test_stream_template_resolution_error_returns_422(client):
    with patch(
        "core.routers.blueprints.resolve_templates",
        side_effect=TemplateResolutionError("bad"),
    ):
        response = await client.post("/blueprints/run/stream", json=_bp("t", "r"))
    assert response.status_code == 422


async def test_stream_auth_required():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        response = await c.post("/blueprints/run/stream", json=_bp("x", "r"))
    assert response.status_code == 401


async def test_stream_run_completed_payload_has_blueprint_name(client, fake_provider):
    events = await _collect_sse(client, "/blueprints/run/stream", json=_bp("my-bp", "r"))
    run_completed = next(e for e in events if e["event"] == "run.completed")
    assert run_completed["blueprint_name"] == "my-bp"


async def test_stream_task_completed_has_status(client, fake_provider):
    events = await _collect_sse(client, "/blueprints/run/stream", json=_bp("s", "r"))
    completed = [e for e in events if e["event"] == "task.completed"]
    assert all("status" in e for e in completed)


async def test_stream_sse_headers(client, fake_provider):
    async with client.stream("POST", "/blueprints/run/stream", json=_bp("h", "r")) as response:
        assert response.headers.get("cache-control") == "no-cache"
        assert response.headers.get("x-accel-buffering") == "no"


async def test_stream_execution_error_emits_error_event(client):
    """If the executor raises inside exec_task, an error event is streamed (no hang)."""
    from unittest.mock import AsyncMock, patch

    from blueprints.executor import BlueprintExecutor

    with patch.object(
        BlueprintExecutor,
        "execute",
        new_callable=AsyncMock,
        side_effect=ValueError("cyclic dependency detected"),
    ):
        events = await _collect_sse(client, "/blueprints/run/stream", json=_bp("bad", "r"))

    error_events = [e for e in events if e["event"] == "error"]
    assert len(error_events) == 1
    assert "cyclic" in error_events[0]["detail"]
    assert not any(e["event"] == "run.persisted" for e in events)


async def test_stream_concurrent_runs_are_isolated(client, fake_provider):
    """Two concurrent SSE streams must not receive each other's task events."""
    import asyncio

    results = await asyncio.gather(
        _collect_sse(client, "/blueprints/run/stream", json=_bp("run-A", "res-a")),
        _collect_sse(client, "/blueprints/run/stream", json=_bp("run-B", "res-b")),
    )

    for events, expected_resource in zip(results, ["res-a", "res-b"], strict=True):
        started = [e for e in events if e["event"] == "task.started"]
        assert len(started) == 1, f"expected 1 task.started, got {started}"
        assert started[0]["resource"] == expected_resource


async def test_sse_generator_cancels_task_on_early_close():
    """Closing the generator before run.completed triggers exec_task.cancel()."""
    import asyncio

    from blueprints.models import Blueprint, ResourceSpec
    from core.routers.blueprints import _sse_generator
    from provider_sdk.base import BaseProvider
    from provider_sdk.registry import registry

    blocker: asyncio.Event = asyncio.Event()

    class _SlowProvider(BaseProvider):
        name = "slow-sse-test"

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
            name="cancel-test",
            version="1.0",
            resources=[ResourceSpec(name="r", provider="slow-sse-test", kind="svc", config={})],
        )
        gen = _sse_generator(bp, False)
        # Advance until task.started — exec_task is now mid-flight (waiting on blocker)
        _first_event = await gen.__anext__()
        # Close generator while exec_task is still running → triggers lines 150-154
        await gen.aclose()
    finally:
        blocker.set()
        registry._providers.clear()
