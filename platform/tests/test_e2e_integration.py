"""
End-to-End Integration Tests

Exercises the full request → blueprint execution → persistence stack using a
FakeProvider that fully implements BaseProvider without any external service
dependencies. Tests cover sequential and parallel execution paths, dependency
semantics, timeout integration, provider failure modes, EventBus propagation,
and run persistence.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx
import pytest
from core.events import event_bus
from core.main import app
from orchestrator.task import TaskStatus
from provider_sdk.base import BaseProvider
from provider_sdk.registry import registry

# ── Configurable FakeProvider ─────────────────────────────────────────────────


class FakeProvider(BaseProvider):
    """Complete BaseProvider implementation for integration testing.

    Tracks every call; optionally simulates connect failures, execute
    exceptions, or slow execution (for timeout tests).
    """

    name = "fake"

    def __init__(
        self,
        *,
        connect_ok: bool = True,
        fail_resources: set[str] | None = None,
        sleep_seconds: float = 0.0,
    ) -> None:
        self.connect_ok = connect_ok
        self.fail_resources: set[str] = fail_resources or set()
        self.sleep_seconds = sleep_seconds
        self.executed: list[str] = []
        self.connect_calls: int = 0
        self.disconnect_calls: int = 0

    async def connect(self) -> bool:
        self.connect_calls += 1
        return self.connect_ok

    async def disconnect(self) -> None:
        self.disconnect_calls += 1

    async def health(self) -> dict[str, Any]:
        return {"status": "ok", "provider": self.name}

    async def list_resources(self) -> list[dict[str, Any]]:
        return []

    async def execute(self, task) -> None:
        if self.sleep_seconds:
            await asyncio.sleep(self.sleep_seconds)
        if task.resource in self.fail_resources:
            raise RuntimeError(f"Simulated failure for {task.resource!r}")
        self.executed.append(task.resource)


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _clear_registry():
    registry._providers.clear()
    yield
    registry._providers.clear()


@pytest.fixture
def fake_provider() -> FakeProvider:
    """Standard always-succeeds FakeProvider, pre-registered."""
    p = FakeProvider()
    registry.register(p)
    return p


@pytest.fixture
async def client():
    """Async HTTP client wired directly to the FastAPI app (no network)."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        headers={"X-API-Key": "test-api-key"},
    ) as c:
        yield c


# ── Helpers ───────────────────────────────────────────────────────────────────


def _bp(name: str, resources: list[dict]) -> dict:
    return {"name": name, "version": "1.0", "resources": resources}


def _res(name: str, **kwargs) -> dict:
    return {"name": name, "provider": "fake", "kind": "svc", "config": {}, **kwargs}


# ── Sequential execution ──────────────────────────────────────────────────────


async def test_sequential_single_resource_succeeds(fake_provider, client):
    r = await client.post("/blueprints/run", json=_bp("seq-single", [_res("alpha")]))
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "seq-single"
    assert len(body["tasks"]) == 1
    assert body["tasks"][0]["resource"] == "alpha"
    assert body["tasks"][0]["status"] == TaskStatus.SUCCESS.value
    assert fake_provider.executed == ["alpha"]


async def test_sequential_multi_resource_all_succeed(fake_provider, client):
    resources = [_res("r1"), _res("r2"), _res("r3")]
    r = await client.post("/blueprints/run", json=_bp("seq-multi", resources))
    assert r.status_code == 200
    tasks = r.json()["tasks"]
    assert len(tasks) == 3
    assert all(t["status"] == TaskStatus.SUCCESS.value for t in tasks)
    assert set(fake_provider.executed) == {"r1", "r2", "r3"}


async def test_sequential_run_provider_connect_called_once_per_task(fake_provider, client):
    resources = [_res("r1"), _res("r2")]
    r = await client.post("/blueprints/run", json=_bp("seq-connect", resources))
    assert r.status_code == 200
    assert fake_provider.connect_calls == 2


async def test_sequential_run_provider_disconnected_after_run(fake_provider, client):
    r = await client.post("/blueprints/run", json=_bp("seq-disconnect", [_res("r1")]))
    assert r.status_code == 200
    assert fake_provider.disconnect_calls == 1


# ── Parallel execution ────────────────────────────────────────────────────────


async def test_parallel_single_resource_succeeds(fake_provider, client):
    r = await client.post("/blueprints/run?parallel=true", json=_bp("par-single", [_res("beta")]))
    assert r.status_code == 200
    body = r.json()
    assert body["tasks"][0]["status"] == TaskStatus.SUCCESS.value
    assert fake_provider.executed == ["beta"]


async def test_parallel_multi_resource_all_succeed(fake_provider, client):
    resources = [_res("p1"), _res("p2"), _res("p3")]
    r = await client.post("/blueprints/run?parallel=true", json=_bp("par-multi", resources))
    assert r.status_code == 200
    tasks = r.json()["tasks"]
    assert all(t["status"] == TaskStatus.SUCCESS.value for t in tasks)
    assert set(fake_provider.executed) == {"p1", "p2", "p3"}


async def test_parallel_diamond_executes_in_waves(client):
    """A → {B, C} → D: A first, B and C in middle wave, D last."""
    execution_order: list[str] = []

    class OrderedFakeProvider(BaseProvider):
        name = "fake"

        async def connect(self) -> bool:
            return True

        async def disconnect(self) -> None:
            pass

        async def health(self) -> dict[str, Any]:
            return {"status": "ok"}

        async def list_resources(self) -> list[dict[str, Any]]:
            return []

        async def execute(self, task) -> None:
            execution_order.append(task.resource)

    registry.register(OrderedFakeProvider())

    bp = _bp(
        "diamond",
        [
            _res("A"),
            _res("B", depends_on=["A"]),
            _res("C", depends_on=["A"]),
            _res("D", depends_on=["B", "C"]),
        ],
    )
    r = await client.post("/blueprints/run?parallel=true", json=bp)
    assert r.status_code == 200
    assert all(t["status"] == TaskStatus.SUCCESS.value for t in r.json()["tasks"])

    assert execution_order[0] == "A"
    assert set(execution_order[1:3]) == {"B", "C"}
    assert execution_order[3] == "D"


# ── Dependency semantics ──────────────────────────────────────────────────────


async def test_depends_on_failure_cascade_sequential(client):
    """A fails → B (depends on A) → C (depends on B): both get SKIPPED_DEPENDENCY_FAILED."""
    registry.register(FakeProvider(fail_resources={"A"}))

    bp = _bp(
        "cascade-seq",
        [
            _res("A"),
            _res("B", depends_on=["A"]),
            _res("C", depends_on=["B"]),
        ],
    )
    r = await client.post("/blueprints/run", json=bp)
    assert r.status_code == 200
    by_resource = {t["resource"]: t["status"] for t in r.json()["tasks"]}
    assert by_resource["A"] == TaskStatus.FAILED.value
    assert by_resource["B"] == TaskStatus.SKIPPED_DEPENDENCY_FAILED.value
    assert by_resource["C"] == TaskStatus.SKIPPED_DEPENDENCY_FAILED.value


async def test_depends_on_failure_cascade_parallel(client):
    """Same cascade semantics apply on the concurrent (Scheduler) path."""
    registry.register(FakeProvider(fail_resources={"A"}))

    bp = _bp(
        "cascade-par",
        [
            _res("A"),
            _res("B", depends_on=["A"]),
            _res("C", depends_on=["B"]),
        ],
    )
    r = await client.post("/blueprints/run?parallel=true", json=bp)
    assert r.status_code == 200
    by_resource = {t["resource"]: t["status"] for t in r.json()["tasks"]}
    assert by_resource["A"] == TaskStatus.FAILED.value
    assert by_resource["B"] == TaskStatus.SKIPPED_DEPENDENCY_FAILED.value
    assert by_resource["C"] == TaskStatus.SKIPPED_DEPENDENCY_FAILED.value


async def test_unaffected_resource_succeeds_despite_sibling_failure(client):
    """A fails → B (depends on A) skipped; C (independent) still succeeds."""
    registry.register(FakeProvider(fail_resources={"A"}))

    bp = _bp(
        "partial-fail",
        [
            _res("A"),
            _res("B", depends_on=["A"]),
            _res("C"),
        ],
    )
    r = await client.post("/blueprints/run", json=bp)
    assert r.status_code == 200
    by_resource = {t["resource"]: t["status"] for t in r.json()["tasks"]}
    assert by_resource["A"] == TaskStatus.FAILED.value
    assert by_resource["B"] == TaskStatus.SKIPPED_DEPENDENCY_FAILED.value
    assert by_resource["C"] == TaskStatus.SUCCESS.value


# ── Provider failure modes ────────────────────────────────────────────────────


async def test_connect_failure_marks_task_failed_sequential(client):
    registry.register(FakeProvider(connect_ok=False))
    r = await client.post("/blueprints/run", json=_bp("conn-fail-seq", [_res("x")]))
    assert r.status_code == 200
    assert r.json()["tasks"][0]["status"] == TaskStatus.FAILED.value


async def test_connect_failure_marks_task_failed_parallel(client):
    registry.register(FakeProvider(connect_ok=False))
    r = await client.post("/blueprints/run?parallel=true", json=_bp("conn-fail-par", [_res("x")]))
    assert r.status_code == 200
    assert r.json()["tasks"][0]["status"] == TaskStatus.FAILED.value


async def test_execute_exception_marks_task_failed_sequential(client):
    registry.register(FakeProvider(fail_resources={"bad"}))
    r = await client.post("/blueprints/run", json=_bp("exec-fail-seq", [_res("bad")]))
    assert r.status_code == 200
    assert r.json()["tasks"][0]["status"] == TaskStatus.FAILED.value


async def test_execute_exception_marks_task_failed_parallel(client):
    registry.register(FakeProvider(fail_resources={"bad"}))
    r = await client.post("/blueprints/run?parallel=true", json=_bp("exec-fail-par", [_res("bad")]))
    assert r.status_code == 200
    assert r.json()["tasks"][0]["status"] == TaskStatus.FAILED.value


async def test_unknown_provider_task_skipped_sequential(client):
    """Resource targeting an unregistered provider → SKIPPED (not FAILED)."""
    bp = {
        "name": "unknown-prov",
        "version": "1.0",
        "resources": [{"name": "thing", "provider": "nonexistent", "kind": "svc", "config": {}}],
    }
    r = await client.post("/blueprints/run", json=bp)
    assert r.status_code == 200
    assert r.json()["tasks"][0]["status"] == TaskStatus.SKIPPED.value


# ── Timeout integration ───────────────────────────────────────────────────────


async def test_timeout_cancel_marks_task_failed_sequential(client):
    """Provider that sleeps 0.3 s with 0.05 s timeout → FAILED (CANCEL strategy)."""
    registry.register(FakeProvider(sleep_seconds=0.3))
    bp = _bp(
        "timeout-seq",
        [_res("slow", timeout_seconds=0.05)],
    )
    r = await client.post("/blueprints/run", json=bp)
    assert r.status_code == 200
    assert r.json()["tasks"][0]["status"] == TaskStatus.FAILED.value


async def test_timeout_cancel_marks_task_failed_parallel(client):
    """Same timeout semantics on the Scheduler path."""
    registry.register(FakeProvider(sleep_seconds=0.3))
    bp = _bp(
        "timeout-par",
        [_res("slow", timeout_seconds=0.05)],
    )
    r = await client.post("/blueprints/run?parallel=true", json=bp)
    assert r.status_code == 200
    assert r.json()["tasks"][0]["status"] == TaskStatus.FAILED.value


async def test_no_timeout_when_task_completes_in_time(client):
    """Provider that sleeps 0.02 s with 1.0 s timeout → SUCCESS."""
    registry.register(FakeProvider(sleep_seconds=0.02))
    bp = _bp(
        "timeout-pass",
        [_res("fast", timeout_seconds=1.0)],
    )
    r = await client.post("/blueprints/run", json=bp)
    assert r.status_code == 200
    assert r.json()["tasks"][0]["status"] == TaskStatus.SUCCESS.value


# ── Persistence and run history ───────────────────────────────────────────────


async def test_run_persisted_and_retrievable_via_api(fake_provider, client):
    """POST /blueprints/run → run_id → GET /runs/{run_id} returns matching record."""
    r = await client.post("/blueprints/run", json=_bp("persist-test", [_res("r1")]))
    assert r.status_code == 200
    body = r.json()
    run_id = body["run_id"]
    assert run_id

    r2 = await client.get(f"/runs/{run_id}")
    assert r2.status_code == 200
    record = r2.json()
    assert record["id"] == run_id
    assert record["blueprint_name"] == "persist-test"
    assert record["parallel"] is False
    assert len(record["tasks"]) == 1
    assert record["tasks"][0]["resource"] == "r1"
    assert record["tasks"][0]["status"] == TaskStatus.SUCCESS.value


async def test_parallel_run_persisted_with_correct_flag(fake_provider, client):
    r = await client.post("/blueprints/run?parallel=true", json=_bp("persist-par", [_res("r1")]))
    assert r.status_code == 200
    run_id = r.json()["run_id"]

    r2 = await client.get(f"/runs/{run_id}")
    assert r2.status_code == 200
    assert r2.json()["parallel"] is True


async def test_failed_task_status_persisted_in_database(client):
    """FAILED status round-trips correctly through the persistence layer."""
    registry.register(FakeProvider(connect_ok=False))
    r = await client.post("/blueprints/run", json=_bp("fail-persist", [_res("broken")]))
    assert r.status_code == 200
    run_id = r.json()["run_id"]

    r2 = await client.get(f"/runs/{run_id}")
    assert r2.status_code == 200
    assert r2.json()["tasks"][0]["status"] == TaskStatus.FAILED.value


async def test_skipped_dependency_failed_status_persisted(client):
    """SKIPPED_DEPENDENCY_FAILED round-trips through persistence (ADR-010)."""
    registry.register(FakeProvider(fail_resources={"A"}))
    r = await client.post(
        "/blueprints/run", json=_bp("skip-persist", [_res("A"), _res("B", depends_on=["A"])])
    )
    assert r.status_code == 200
    run_id = r.json()["run_id"]

    r2 = await client.get(f"/runs/{run_id}")
    assert r2.status_code == 200
    by_resource = {t["resource"]: t["status"] for t in r2.json()["tasks"]}
    assert by_resource["B"] == TaskStatus.SKIPPED_DEPENDENCY_FAILED.value


async def test_run_appears_in_list_endpoint(fake_provider, client):
    """A completed run appears in GET /runs."""
    r = await client.post("/blueprints/run", json=_bp("list-me", [_res("r1")]))
    assert r.status_code == 200
    run_id = r.json()["run_id"]

    r2 = await client.get("/runs")
    assert r2.status_code == 200
    ids = [run["id"] for run in r2.json()]
    assert run_id in ids


async def test_multiple_runs_all_listed(fake_provider, client):
    """Three sequential runs are all returned by GET /runs."""
    run_ids = set()
    for name in ("run-alpha", "run-beta", "run-gamma"):
        r = await client.post("/blueprints/run", json=_bp(name, [_res("r1")]))
        assert r.status_code == 200
        run_ids.add(r.json()["run_id"])

    r2 = await client.get("/runs")
    assert r2.status_code == 200
    listed_ids = {run["id"] for run in r2.json()}
    assert run_ids.issubset(listed_ids)


# ── EventBus integration ──────────────────────────────────────────────────────


async def test_eventbus_fires_task_and_run_events_sequential(fake_provider, client):
    """task.started, task.completed, and run.completed all fire during a sequential run."""
    events: list[tuple[str, dict]] = []

    event_bus.subscribe("task.started", lambda p: events.append(("started", p)))
    event_bus.subscribe("task.completed", lambda p: events.append(("completed", p)))
    event_bus.subscribe("run.completed", lambda p: events.append(("run.completed", p)))

    bp = _bp("events-seq", [_res("e1"), _res("e2")])
    r = await client.post("/blueprints/run", json=bp)
    assert r.status_code == 200

    started = [e for e in events if e[0] == "started"]
    completed = [e for e in events if e[0] == "completed"]
    run_complete = [e for e in events if e[0] == "run.completed"]

    assert len(started) == 2
    assert len(completed) == 2
    assert len(run_complete) == 1

    resources_started = {e[1]["resource"] for e in started}
    assert resources_started == {"e1", "e2"}


async def test_eventbus_fires_task_and_run_events_parallel(fake_provider, client):
    """Same EventBus contract holds on the parallel (Scheduler) execution path."""
    events: list[tuple[str, dict]] = []

    event_bus.subscribe("task.started", lambda p: events.append(("started", p)))
    event_bus.subscribe("task.completed", lambda p: events.append(("completed", p)))
    event_bus.subscribe("run.completed", lambda p: events.append(("run.completed", p)))

    bp = _bp("events-par", [_res("e1"), _res("e2")])
    r = await client.post("/blueprints/run?parallel=true", json=bp)
    assert r.status_code == 200

    assert sum(1 for e in events if e[0] == "started") == 2
    assert sum(1 for e in events if e[0] == "completed") == 2
    assert sum(1 for e in events if e[0] == "run.completed") == 1


async def test_eventbus_fires_for_failed_tasks_too(client):
    """task.completed fires even when the task fails — consumers must handle any status."""
    registry.register(FakeProvider(fail_resources={"bad"}))

    completed_statuses: list[str] = []
    event_bus.subscribe("task.completed", lambda p: completed_statuses.append(p["status"]))

    r = await client.post("/blueprints/run", json=_bp("fail-events", [_res("bad")]))
    assert r.status_code == 200
    assert TaskStatus.FAILED.value in completed_statuses


# ── Blueprint plan endpoint ───────────────────────────────────────────────────


async def test_plan_endpoint_returns_dependency_ordered_steps(fake_provider, client):
    """POST /blueprints/plan returns steps in dependency-respecting order."""
    bp = _bp(
        "plan-order",
        [
            _res("second", depends_on=["first"]),
            _res("first"),
        ],
    )
    r = await client.post("/blueprints/plan", json=bp)
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "plan-order"
    step_names = [s["resource"] for s in body["steps"]]
    assert step_names.index("first") < step_names.index("second")


async def test_plan_endpoint_includes_depends_on_in_steps(client):
    """Steps returned by /blueprints/plan carry through the depends_on field."""
    bp = _bp("plan-deps", [_res("A"), _res("B", depends_on=["A"])])
    r = await client.post("/blueprints/plan", json=bp)
    assert r.status_code == 200
    steps = {s["resource"]: s for s in r.json()["steps"]}
    assert steps["B"]["depends_on"] == ["A"]
    assert steps["A"]["depends_on"] == []
