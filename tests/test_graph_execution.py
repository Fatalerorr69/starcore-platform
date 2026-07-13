"""
Blueprint Graph Execution Tests
"""

from __future__ import annotations

from pathlib import Path

import pytest
from blueprints.loader import BlueprintLoader
from blueprints.models import Blueprint, ResourceSpec
from blueprints.planner import ExecutionPlanner
from orchestrator.scheduler import Scheduler
from orchestrator.task import TaskStatus
from provider_sdk.base import BaseProvider
from provider_sdk.registry import registry

GRAPH_EXAMPLE_PATH = (
    Path(__file__).parent.parent / "packages" / "blueprints" / "examples" / "graph.yaml"
)


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


def test_resource_spec_defaults_depends_on_to_empty_list():
    spec = ResourceSpec(name="a", provider="fake", kind="svc", config={})
    assert spec.depends_on == []


def test_create_graph_builds_tasks_with_dependencies():
    blueprint = Blueprint(
        name="graph-test",
        resources=[
            ResourceSpec(name="a", provider="fake", kind="svc", config={}),
            ResourceSpec(name="b", provider="fake", kind="svc", config={}, depends_on=["a"]),
        ],
    )
    graph = ExecutionPlanner().create_graph(blueprint)

    assert graph.get("a").depends_on == []
    assert graph.get("b").depends_on == ["a"]


def test_create_graph_rejects_unknown_dependency():
    blueprint = Blueprint(
        name="graph-test",
        resources=[
            ResourceSpec(name="a", provider="fake", kind="svc", config={}, depends_on=["ghost"]),
        ],
    )
    with pytest.raises(ValueError):
        ExecutionPlanner().create_graph(blueprint)


def test_graph_yaml_example_loads_with_dependencies():
    blueprint = BlueprintLoader.load(GRAPH_EXAMPLE_PATH)
    by_name = {r.name: r for r in blueprint.resources}
    assert by_name["web-vm"].depends_on == ["db", "cache"]
    assert by_name["db"].depends_on == []


async def test_scheduler_executes_blueprint_graph_respecting_dependencies():
    fake = FakeProvider()
    registry.register(fake)

    blueprint = Blueprint(
        name="graph-run-test",
        resources=[
            ResourceSpec(name="a", provider="fake", kind="svc", config={}),
            ResourceSpec(name="b", provider="fake", kind="svc", config={}),
            ResourceSpec(
                name="c",
                provider="fake",
                kind="svc",
                config={},
                depends_on=["a", "b"],
            ),
        ],
    )
    graph = ExecutionPlanner().create_graph(blueprint)
    tasks = await Scheduler().execute(graph)

    assert all(task.status == TaskStatus.SUCCESS for task in tasks)
    assert fake.order.index("c") > fake.order.index("a")
    assert fake.order.index("c") > fake.order.index("b")
