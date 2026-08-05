"""
PostgreSQL dialect smoke tests.

Verify that the STARCORE Platform works end-to-end with a real PostgreSQL
database: migrations, API persistence, and key query paths. These tests
run only in CI when STARCORE_TEST_POSTGRES_URL is set.

Skipped automatically in the standard SQLite suite.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from core.main import app
from provider_sdk.base import BaseProvider
from provider_sdk.registry import registry

# ── Minimal fake provider ──────────────────────────────────────────────────


class _FakeProvider(BaseProvider):
    name = "fake"

    def __init__(self) -> None:
        self.executed: list[str] = []

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> None:
        pass

    async def health(self) -> dict[str, Any]:
        return {"status": "ok", "provider": self.name}

    async def list_resources(self) -> list[dict[str, Any]]:
        return []

    async def execute(self, task) -> None:
        self.executed.append(task.resource)


# ── Shared helpers ─────────────────────────────────────────────────────────


def _res(name: str, **kwargs) -> dict:
    return {"name": name, "provider": "fake", "kind": "svc", "config": {}, **kwargs}


def _bp(name: str, resources: list[dict]) -> dict:
    return {"name": name, "version": "1.0", "resources": resources}


@pytest.fixture
def fake_provider() -> _FakeProvider:
    p = _FakeProvider()
    registry.register(p)
    return p


@pytest.fixture
async def client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        headers={"X-API-Key": "test-api-key"},
    ) as c:
        yield c


# ── Health ─────────────────────────────────────────────────────────────────


async def test_health_returns_healthy_with_postgres(client):
    """/health must report 'healthy' when backed by PostgreSQL."""
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "database" in body


# ── Blueprint plan (stateless) ─────────────────────────────────────────────


async def test_plan_blueprint_returns_sorted_steps(client, fake_provider):
    """POST /blueprints/plan must resolve topological order with PostgreSQL backend."""
    payload = _bp(
        "pg-plan",
        [
            _res("b", depends_on=["a"]),
            _res("a"),
        ],
    )
    response = await client.post("/blueprints/plan", json=payload)
    assert response.status_code == 200
    steps = response.json()["steps"]
    names = [s["resource"] for s in steps]
    assert names.index("a") < names.index("b")


# ── Sequential execution + persistence ────────────────────────────────────


async def test_sequential_run_persists_to_postgres(client, fake_provider):
    """POST /blueprints/run must persist run record and task rows in PostgreSQL."""
    payload = _bp("pg-seq", [_res("alpha"), _res("beta")])
    response = await client.post("/blueprints/run", json=payload)
    assert response.status_code == 200
    body = response.json()
    run_id = body["run_id"]
    assert run_id
    assert len(body["tasks"]) == 2
    assert all(t["status"] == "completed" for t in body["tasks"])

    # Verify via /runs/{id} that data was persisted correctly to PostgreSQL
    detail = await client.get(f"/runs/{run_id}")
    assert detail.status_code == 200
    d = detail.json()
    assert d["id"] == run_id
    assert d["blueprint_name"] == "pg-seq"
    assert d["parallel"] is False
    assert len(d["tasks"]) == 2
    assert all(t["status"] == "completed" for t in d["tasks"])


# ── Parallel execution + persistence ──────────────────────────────────────


async def test_parallel_run_persists_to_postgres(client, fake_provider):
    """POST /blueprints/run?parallel=true must persist parallel=True in PostgreSQL."""
    payload = _bp("pg-par", [_res("x"), _res("y")])
    response = await client.post("/blueprints/run", json=payload, params={"parallel": "true"})
    assert response.status_code == 200
    body = response.json()
    run_id = body["run_id"]

    detail = await client.get(f"/runs/{run_id}")
    assert detail.status_code == 200
    assert detail.json()["parallel"] is True


# ── Runs list ──────────────────────────────────────────────────────────────


async def test_list_runs_returns_all_persisted_runs(client, fake_provider):
    """GET /runs must return both sequential and parallel runs from PostgreSQL."""
    await client.post("/blueprints/run", json=_bp("run-a", [_res("r1")]))
    await client.post(
        "/blueprints/run",
        json=_bp("run-b", [_res("r2")]),
        params={"parallel": "true"},
    )

    response = await client.get("/runs")
    assert response.status_code == 200
    runs = response.json()
    names = {r["blueprint_name"] for r in runs}
    assert "run-a" in names
    assert "run-b" in names


async def test_list_runs_404_for_unknown_id(client):
    """GET /runs/{id} with a non-existent ID must return 404."""
    response = await client.get("/runs/00000000-does-not-exist")
    assert response.status_code == 404


# ── Dependency failure persistence ─────────────────────────────────────────


async def test_failed_dependency_status_persisted_to_postgres(client):
    """SKIPPED_DEPENDENCY_FAILED status must be persisted correctly in PostgreSQL."""

    # Use a provider that raises on execute
    class _FailProvider(_FakeProvider):
        async def execute(self, task) -> None:
            raise RuntimeError("simulated failure")

    fail_p = _FailProvider()
    registry.register(fail_p)

    payload = _bp(
        "pg-dep-fail",
        [
            _res("root"),
            _res("child", depends_on=["root"]),
        ],
    )
    response = await client.post("/blueprints/run", json=payload)
    assert response.status_code == 200
    body = response.json()
    run_id = body["run_id"]

    # Verify statuses persisted to PostgreSQL
    detail = await client.get(f"/runs/{run_id}")
    assert detail.status_code == 200
    tasks_by_name = {t["resource"]: t for t in detail.json()["tasks"]}

    assert tasks_by_name["root"]["status"] == "failed"
    assert tasks_by_name["child"]["status"] == "skipped_dependency_failed"


# ── Pagination ─────────────────────────────────────────────────────────────


async def test_list_runs_pagination(client, fake_provider):
    """GET /runs with limit/offset must work correctly against PostgreSQL."""
    for i in range(5):
        await client.post("/blueprints/run", json=_bp(f"run-{i}", [_res("r")]))

    all_runs = (await client.get("/runs")).json()
    assert len(all_runs) == 5

    page_1 = (await client.get("/runs", params={"limit": 2, "offset": 0})).json()
    page_2 = (await client.get("/runs", params={"limit": 2, "offset": 2})).json()
    page_3 = (await client.get("/runs", params={"limit": 2, "offset": 4})).json()

    assert len(page_1) == 2
    assert len(page_2) == 2
    assert len(page_3) == 1

    # No duplicates across pages
    all_ids = [r["id"] for r in page_1 + page_2 + page_3]
    assert len(all_ids) == len(set(all_ids))


# ── Direct repository layer ────────────────────────────────────────────────


def test_repository_save_and_retrieve(fake_provider):
    """save_run / list_runs / get_run must work against a live PostgreSQL database."""
    from core.database import get_session
    from core.repository import get_run, list_runs, save_run
    from orchestrator.task import Task, TaskStatus
    from orchestrator.task_graph import TaskGraph

    graph = TaskGraph()
    graph.add_task(
        Task(
            id="t-pg-1",
            provider="fake",
            resource="db-resource",
            action="create",
            kind="svc",
            status=TaskStatus.SUCCESS,
            result={"rows": 42},
        )
    )

    session = get_session()
    try:
        record = save_run(session, "pg-repo-test", "2.0", False, list(graph.tasks.values()))
        run_id = record.id

        retrieved = get_run(session, run_id)
        assert retrieved is not None
        assert retrieved.blueprint_name == "pg-repo-test"
        assert retrieved.version == "2.0"
        assert len(retrieved.tasks) == 1
        assert retrieved.tasks[0].resource == "db-resource"
        assert retrieved.tasks[0].result == {"rows": 42}

        all_runs = list_runs(session, limit=10)
        assert any(r.id == run_id for r in all_runs)
    finally:
        session.close()
