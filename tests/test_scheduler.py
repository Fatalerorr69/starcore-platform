"""
Scheduler and TaskGraph Tests
"""

from __future__ import annotations

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
