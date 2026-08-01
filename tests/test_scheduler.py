"""
Scheduler and TaskGraph Tests
"""

from __future__ import annotations

import asyncio

import pytest
from orchestrator.scheduler import Scheduler
from orchestrator.task import Task, TaskStatus
from orchestrator.task_graph import TaskGraph
from provider_sdk.base import BaseProvider
from provider_sdk.registry import registry


class FakeProvider(BaseProvider):
    name = "fake"

    def __init__(self) -> None:
        self.order: list[str] = []

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> None:
        return None

    async def health(self) -> dict:
        return {"status": "ok", "provider": self.name}

    async def list_resources(self) -> list[dict]:
        return []

    async def execute(self, task) -> None:
        self.order.append(task.resource)


class LockAwareFakeProvider(BaseProvider):
    """A provider that performs real (slow) connection work exactly once,
    using :attr:`BaseProvider._connect_lock` the way a real provider
    (:class:`~providers.docker.provider.DockerProvider`,
    :class:`~providers.proxmox.provider.ProxmoxProvider`) does.

    Used to prove, at the ``Scheduler`` integration level, that RISK-01 /
    TD-02 is closed: even though ``Scheduler._run_task`` still calls
    ``connect()`` once per task, the underlying connection work only
    actually happens once per provider instance, no matter how many tasks
    in the same wave target it.
    """

    name = "fake"

    def __init__(self) -> None:
        self.order: list[str] = []
        self.connect_calls = 0
        self.real_connect_calls = 0
        self._connected = False

    async def connect(self) -> bool:
        self.connect_calls += 1
        async with self._connect_lock:
            if self._connected:
                return True
            self.real_connect_calls += 1
            await asyncio.sleep(0.05)  # widen the concurrency window
            self._connected = True
            return True

    async def disconnect(self) -> None:
        self._connected = False

    async def health(self) -> dict:
        return {"status": "ok", "provider": self.name}

    async def list_resources(self) -> list[dict]:
        return []

    async def execute(self, task) -> None:
        self.order.append(task.resource)


@pytest.fixture(autouse=True)
def clean_registry():
    registry._providers.clear()
    yield
    registry._providers.clear()


def test_task_graph_tracks_dependencies():
    graph = TaskGraph()
    a = Task(id="a", provider="fake", action="create", resource="a")
    b = Task(id="b", provider="fake", action="create", resource="b", depends_on=["a"])
    graph.add_task(a)
    graph.add_task(b)

    assert graph.get("a") is a
    assert {t.id for t in graph.all()} == {"a", "b"}
    assert graph.dependents_of("a") == {"b"}


async def test_scheduler_respects_dependency_order():
    fake = FakeProvider()
    registry.register(fake)

    graph = TaskGraph()
    a = Task(id="a", provider="fake", action="create", resource="a")
    b = Task(id="b", provider="fake", action="create", resource="b", depends_on=["a"])
    graph.add_task(a)
    graph.add_task(b)

    tasks = await Scheduler().execute(graph)

    assert all(task.status == TaskStatus.SUCCESS for task in tasks)
    assert fake.order.index("a") < fake.order.index("b")


async def test_scheduler_runs_independent_tasks_concurrently():
    fake = FakeProvider()
    registry.register(fake)

    graph = TaskGraph()
    a = Task(id="a", provider="fake", action="create", resource="a")
    b = Task(id="b", provider="fake", action="create", resource="b")
    graph.add_task(a)
    graph.add_task(b)

    tasks = await Scheduler().execute(graph)

    assert all(task.status == TaskStatus.SUCCESS for task in tasks)


async def test_scheduler_connects_shared_provider_exactly_once_per_wave():
    """RISK-01 / TD-02 regression test.

    Two independent tasks (no ``depends_on`` between them) targeting the
    same provider land in the same scheduler wave and are dispatched
    concurrently via ``asyncio.gather`` (see ``Scheduler.execute``). Before
    the fix, both would race to reassign the provider's shared, unguarded
    ``self._client``. After the fix, ``connect()`` is still called once per
    task (unchanged Scheduler behavior), but the actual connection work
    happens exactly once per provider instance.
    """
    fake = LockAwareFakeProvider()
    registry.register(fake)

    graph = TaskGraph()
    a = Task(id="a", provider="fake", action="create", resource="a")
    b = Task(id="b", provider="fake", action="create", resource="b")
    graph.add_task(a)
    graph.add_task(b)

    tasks = await Scheduler().execute(graph)

    assert all(task.status == TaskStatus.SUCCESS for task in tasks)
    assert fake.connect_calls == 2  # Scheduler still calls connect() per task.
    assert fake.real_connect_calls == 1  # But the real work happens once.
    assert set(fake.order) == {"a", "b"}


async def test_scheduler_skips_unregistered_provider():
    graph = TaskGraph()
    a = Task(id="a", provider="ghost", action="create", resource="a")
    graph.add_task(a)

    tasks = await Scheduler().execute(graph)

    assert tasks[0].status == TaskStatus.SKIPPED


async def test_scheduler_emits_run_completed_event():
    from core.events import event_bus

    received = []

    async def handler(payload):
        received.append(payload)

    event_bus.subscribe("run.completed", handler)

    fake = FakeProvider()
    registry.register(fake)

    graph = TaskGraph()
    a = Task(id="a", provider="fake", action="create", resource="a")
    graph.add_task(a)

    await Scheduler().execute(graph)

    assert len(received) == 1


async def test_scheduler_stalls_when_dependency_is_never_satisfied():
    """Lines 37-44: stall detection — task depends on a missing id."""
    fake = FakeProvider()
    registry.register(fake)

    graph = TaskGraph()
    b = Task(id="b", provider="fake", action="create", resource="b", depends_on=["ghost"])
    graph.add_task(b)

    tasks = await Scheduler().execute(graph)

    assert tasks[0].status == TaskStatus.FAILED


async def test_scheduler_marks_task_failed_when_execute_raises():
    """Lines 98-100: exception in provider.execute() is caught and task marked failed."""

    class _RaisingProvider(BaseProvider):
        name = "raiser"

        async def connect(self) -> bool:
            return True

        async def disconnect(self) -> None:
            pass

        async def health(self) -> dict:
            return {"status": "ok", "provider": self.name}

        async def list_resources(self) -> list[dict]:
            return []

        async def execute(self, task) -> None:
            raise RuntimeError("simulated execute failure")

    registry.register(_RaisingProvider())

    graph = TaskGraph()
    a = Task(id="a", provider="raiser", action="create", resource="a")
    graph.add_task(a)

    tasks = await Scheduler().execute(graph)

    assert tasks[0].status == TaskStatus.FAILED


async def test_scheduler_skips_dependent_after_dependency_fails():
    """ADR-010: depends_on is a success gate, not just an ordering
    constraint. Scheduler must never call provider.execute() for a task
    whose declared dependency did not reach SUCCESS.
    """

    class _RaisingProvider(BaseProvider):
        name = "raiser"

        async def connect(self) -> bool:
            return True

        async def disconnect(self) -> None:
            pass

        async def health(self) -> dict:
            return {"status": "ok", "provider": self.name}

        async def list_resources(self) -> list[dict]:
            return []

        async def execute(self, task) -> None:
            raise RuntimeError("simulated dependency failure")

    fake = FakeProvider()
    registry.register(fake)
    registry.register(_RaisingProvider())

    graph = TaskGraph()
    a = Task(id="a", provider="raiser", action="create", resource="a")
    b = Task(id="b", provider="fake", action="create", resource="b", depends_on=["a"])
    graph.add_task(a)
    graph.add_task(b)

    tasks = await Scheduler().execute(graph)

    by_id = {t.id: t for t in tasks}
    assert by_id["a"].status == TaskStatus.FAILED
    assert by_id["b"].status == TaskStatus.SKIPPED_DEPENDENCY_FAILED
    assert fake.order == []


async def test_scheduler_skips_transitively_through_a_dependency_chain():
    """A fails; B depends on A; C depends on B. Both B and C must be
    skipped in the same run -- propagation must not stop after one hop,
    even though B and C are dispatched in different waves.
    """

    class _RaisingProvider(BaseProvider):
        name = "raiser"

        async def connect(self) -> bool:
            return True

        async def disconnect(self) -> None:
            pass

        async def health(self) -> dict:
            return {"status": "ok", "provider": self.name}

        async def list_resources(self) -> list[dict]:
            return []

        async def execute(self, task) -> None:
            raise RuntimeError("simulated dependency failure")

    fake = FakeProvider()
    registry.register(fake)
    registry.register(_RaisingProvider())

    graph = TaskGraph()
    a = Task(id="a", provider="raiser", action="create", resource="a")
    b = Task(id="b", provider="fake", action="create", resource="b", depends_on=["a"])
    c = Task(id="c", provider="fake", action="create", resource="c", depends_on=["b"])
    graph.add_task(a)
    graph.add_task(b)
    graph.add_task(c)

    tasks = await Scheduler().execute(graph)

    by_id = {t.id: t for t in tasks}
    assert by_id["a"].status == TaskStatus.FAILED
    assert by_id["b"].status == TaskStatus.SKIPPED_DEPENDENCY_FAILED
    assert by_id["c"].status == TaskStatus.SKIPPED_DEPENDENCY_FAILED
    assert fake.order == []


async def test_scheduler_skips_dependent_with_multiple_failed_dependencies():
    """A dependent with two failed dependencies must still be skipped
    exactly once, not raise or double-dispatch."""

    class _RaisingProvider(BaseProvider):
        name = "raiser"

        async def connect(self) -> bool:
            return True

        async def disconnect(self) -> None:
            pass

        async def health(self) -> dict:
            return {"status": "ok", "provider": self.name}

        async def list_resources(self) -> list[dict]:
            return []

        async def execute(self, task) -> None:
            raise RuntimeError("simulated dependency failure")

    fake = FakeProvider()
    registry.register(fake)
    registry.register(_RaisingProvider())

    graph = TaskGraph()
    a = Task(id="a", provider="raiser", action="create", resource="a")
    b = Task(id="b", provider="raiser", action="create", resource="b")
    c = Task(id="c", provider="fake", action="create", resource="c", depends_on=["a", "b"])
    graph.add_task(a)
    graph.add_task(b)
    graph.add_task(c)

    tasks = await Scheduler().execute(graph)

    by_id = {t.id: t for t in tasks}
    assert by_id["a"].status == TaskStatus.FAILED
    assert by_id["b"].status == TaskStatus.FAILED
    assert by_id["c"].status == TaskStatus.SKIPPED_DEPENDENCY_FAILED
    assert fake.order == []


async def test_scheduler_runs_dependent_when_dependency_succeeds():
    """Sanity check for the ADR-010 gate: a dependent must still run
    normally, in the same wave-ordering as before, when its dependency
    actually succeeds.
    """
    fake = FakeProvider()
    registry.register(fake)

    graph = TaskGraph()
    a = Task(id="a", provider="fake", action="create", resource="a")
    b = Task(id="b", provider="fake", action="create", resource="b", depends_on=["a"])
    graph.add_task(a)
    graph.add_task(b)

    tasks = await Scheduler().execute(graph)

    by_id = {t.id: t for t in tasks}
    assert by_id["a"].status == TaskStatus.SUCCESS
    assert by_id["b"].status == TaskStatus.SUCCESS
    assert fake.order.index("a") < fake.order.index("b")


async def test_scheduler_skips_convergence_point_of_diamond_when_one_branch_fails():
    """Diamond graph: base -> {left, right} -> tip, across two waves. `left`
    fails; `right` succeeds. `tip` depends on both, so it must be skipped
    even though one of its two dependencies succeeded.
    """

    class _RaisingProvider(BaseProvider):
        name = "raiser"

        async def connect(self) -> bool:
            return True

        async def disconnect(self) -> None:
            pass

        async def health(self) -> dict:
            return {"status": "ok", "provider": self.name}

        async def list_resources(self) -> list[dict]:
            return []

        async def execute(self, task) -> None:
            raise RuntimeError("simulated dependency failure")

    fake = FakeProvider()
    registry.register(fake)
    registry.register(_RaisingProvider())

    graph = TaskGraph()
    base = Task(id="base", provider="fake", action="create", resource="base")
    left = Task(id="left", provider="raiser", action="create", resource="left", depends_on=["base"])
    right = Task(
        id="right", provider="fake", action="create", resource="right", depends_on=["base"]
    )
    tip = Task(
        id="tip", provider="fake", action="create", resource="tip", depends_on=["left", "right"]
    )
    graph.add_task(base)
    graph.add_task(left)
    graph.add_task(right)
    graph.add_task(tip)

    tasks = await Scheduler().execute(graph)

    by_id = {t.id: t for t in tasks}
    assert by_id["base"].status == TaskStatus.SUCCESS
    assert by_id["left"].status == TaskStatus.FAILED
    assert by_id["right"].status == TaskStatus.SUCCESS
    assert by_id["tip"].status == TaskStatus.SKIPPED_DEPENDENCY_FAILED
    assert fake.order == ["base", "right"]


async def test_scheduler_marks_task_failed_when_connect_returns_false():
    """Lines 87-94: connect() returns False → task marked FAILED without calling execute."""

    class _FailingConnectProvider(BaseProvider):
        name = "failconn"

        async def connect(self) -> bool:
            return False

        async def disconnect(self) -> None:
            pass

        async def health(self) -> dict:
            return {"status": "disconnected", "provider": self.name}

        async def list_resources(self) -> list[dict]:
            return []

        async def execute(self, task) -> None:
            raise AssertionError("execute must not be called when connect fails")

    registry.register(_FailingConnectProvider())

    graph = TaskGraph()
    a = Task(id="a", provider="failconn", action="create", resource="a")
    graph.add_task(a)

    tasks = await Scheduler().execute(graph)

    assert tasks[0].status == TaskStatus.FAILED


# ---------------------------------------------------------------------------
# timeout_seconds — scheduler integration
# ---------------------------------------------------------------------------


async def test_scheduler_succeeds_when_task_completes_before_timeout():
    fake = FakeProvider()
    registry.register(fake)

    graph = TaskGraph()
    graph.add_task(
        Task(id="a", provider="fake", action="create", resource="a", timeout_seconds=10.0)
    )

    tasks = await Scheduler().execute(graph)
    assert tasks[0].status == TaskStatus.SUCCESS


async def test_scheduler_marks_failed_when_timeout_exceeded():
    class _SlowProvider(BaseProvider):
        name = "slow-sched"

        async def connect(self) -> bool:
            return True

        async def disconnect(self) -> None:
            return None

        async def health(self) -> dict:
            return {"status": "ok"}

        async def list_resources(self) -> list[dict]:
            return []

        async def execute(self, task) -> None:
            await asyncio.sleep(10)

    registry.register(_SlowProvider())

    graph = TaskGraph()
    graph.add_task(
        Task(id="a", provider="slow-sched", action="create", resource="a", timeout_seconds=0.01)
    )

    tasks = await Scheduler().execute(graph)
    assert tasks[0].status == TaskStatus.FAILED
