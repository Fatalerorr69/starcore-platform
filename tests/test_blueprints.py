"""
Blueprint Engine Tests
"""

from __future__ import annotations

from pathlib import Path

import pytest
from blueprints.executor import BlueprintExecutor
from blueprints.loader import BlueprintLoader
from blueprints.models import Blueprint, ResourceSpec
from blueprints.planner import ExecutionPlanner
from orchestrator.task import TaskStatus
from provider_sdk.base import BaseProvider
from provider_sdk.registry import registry

EXAMPLE_PATH = Path(__file__).parent.parent / "packages" / "blueprints" / "examples" / "basic.yaml"


class FakeProvider(BaseProvider):
    name = "fake"

    def __init__(self, connect_result: bool = True) -> None:
        self._connect_result = connect_result
        self.executed = []

    async def connect(self) -> bool:
        return self._connect_result

    async def disconnect(self) -> None:
        return None

    async def health(self) -> dict:
        return {"status": "ok", "provider": self.name}

    async def list_resources(self) -> list[dict]:
        return []

    async def execute(self, task) -> None:
        self.executed.append(task.resource)


@pytest.fixture(autouse=True)
def clean_registry():
    registry._providers.clear()
    yield
    registry._providers.clear()


def test_loader_loads_basic_blueprint():
    blueprint = BlueprintLoader.load(EXAMPLE_PATH)
    assert blueprint.name == "demo"
    assert len(blueprint.resources) == 2
    assert blueprint.resources[0].provider == "proxmox"
    assert blueprint.resources[1].provider == "docker"


def test_planner_creates_plan_from_blueprint():
    blueprint = BlueprintLoader.load(EXAMPLE_PATH)
    plan = ExecutionPlanner().create_plan(blueprint)
    assert len(plan) == 2
    assert plan[0]["resource"] == "web-vm"
    assert plan[1]["resource"] == "postgres"


async def test_executor_runs_blueprint_with_fake_provider():
    fake = FakeProvider(connect_result=True)
    registry.register(fake)

    blueprint = Blueprint(
        name="fake-test",
        resources=[ResourceSpec(name="thing", provider="fake", kind="svc", config={})],
    )
    tasks = await BlueprintExecutor().execute(blueprint)

    assert len(tasks) == 1
    assert tasks[0].status == TaskStatus.SUCCESS
    assert fake.executed == ["thing"]


async def test_executor_marks_failed_connect_as_failed():
    fake = FakeProvider(connect_result=False)
    registry.register(fake)

    blueprint = Blueprint(
        name="fake-fail-test",
        resources=[ResourceSpec(name="thing", provider="fake", kind="svc", config={})],
    )
    tasks = await BlueprintExecutor().execute(blueprint)

    assert len(tasks) == 1
    assert tasks[0].status == TaskStatus.FAILED


async def test_executor_skips_unknown_provider():
    blueprint = Blueprint(
        name="unknown-provider-test",
        resources=[
            ResourceSpec(name="ghost", provider="does-not-exist", kind="vm", config={}),
        ],
    )
    tasks = await BlueprintExecutor().execute(blueprint)

    assert len(tasks) == 1
    assert tasks[0].status == TaskStatus.SKIPPED


def test_lxc_example_loads_with_lxc_kind():
    lxc_path = Path(__file__).parent.parent / "packages" / "blueprints" / "examples" / "lxc.yaml"
    blueprint = BlueprintLoader.load(lxc_path)
    assert blueprint.resources[0].kind == "lxc"


async def test_executor_respects_dependency_order_despite_declaration_order():
    """RISK-02 / TD-01 regression test.

    A resource declared *before* its dependency in the YAML/blueprint must
    still be executed *after* it, even on the default sequential path
    (no ``--parallel``). Before the fix, ``BlueprintExecutor`` iterated the
    plan strictly in file-declaration order and ignored ``depends_on``
    entirely.
    """
    fake = FakeProvider()
    registry.register(fake)

    blueprint = Blueprint(
        name="dependency-order-test",
        resources=[
            # Declared first, but depends on "db" which is declared second.
            ResourceSpec(
                name="app",
                provider="fake",
                kind="svc",
                config={},
                depends_on=["db"],
            ),
            ResourceSpec(name="db", provider="fake", kind="svc", config={}),
        ],
    )

    tasks = await BlueprintExecutor().execute(blueprint)

    assert all(task.status == TaskStatus.SUCCESS for task in tasks)
    assert fake.executed.index("db") < fake.executed.index("app")


def test_planner_create_plan_preserves_declaration_order_without_dependencies():
    """Backward-compatibility guarantee: no depends_on -> no reordering."""
    blueprint = BlueprintLoader.load(EXAMPLE_PATH)
    plan = ExecutionPlanner().create_plan(blueprint)

    assert [step["resource"] for step in plan] == ["web-vm", "postgres"]


def test_planner_create_plan_orders_diamond_dependency_correctly():
    blueprint = Blueprint(
        name="diamond-test",
        resources=[
            # Declared out of order on purpose: "c" first, its dependencies after.
            ResourceSpec(name="c", provider="fake", kind="svc", config={}, depends_on=["a", "b"]),
            ResourceSpec(name="a", provider="fake", kind="svc", config={}),
            ResourceSpec(name="b", provider="fake", kind="svc", config={}),
        ],
    )

    plan = ExecutionPlanner().create_plan(blueprint)
    order = [step["resource"] for step in plan]

    assert order.index("c") > order.index("a")
    assert order.index("c") > order.index("b")
    assert set(order) == {"a", "b", "c"}


def test_planner_create_plan_rejects_unknown_dependency():
    blueprint = Blueprint(
        name="unknown-dependency-test",
        resources=[
            ResourceSpec(name="a", provider="fake", kind="svc", config={}, depends_on=["ghost"]),
        ],
    )

    with pytest.raises(ValueError, match="unknown resource"):
        ExecutionPlanner().create_plan(blueprint)


def test_planner_create_plan_rejects_circular_dependency():
    blueprint = Blueprint(
        name="cycle-test",
        resources=[
            ResourceSpec(name="a", provider="fake", kind="svc", config={}, depends_on=["b"]),
            ResourceSpec(name="b", provider="fake", kind="svc", config={}, depends_on=["a"]),
        ],
    )

    with pytest.raises(ValueError, match="circular dependency"):
        ExecutionPlanner().create_plan(blueprint)


def test_planner_create_plan_rejects_self_dependency():
    blueprint = Blueprint(
        name="self-cycle-test",
        resources=[
            ResourceSpec(name="a", provider="fake", kind="svc", config={}, depends_on=["a"]),
        ],
    )

    with pytest.raises(ValueError, match="circular dependency"):
        ExecutionPlanner().create_plan(blueprint)


async def test_executor_emits_run_completed_event():
    from core.events import event_bus

    received = []

    async def handler(payload):
        received.append(payload)

    event_bus.subscribe("run.completed", handler)

    fake = FakeProvider()
    registry.register(fake)

    blueprint = Blueprint(
        name="event-test",
        resources=[ResourceSpec(name="thing", provider="fake", kind="svc", config={})],
    )

    await BlueprintExecutor().execute(blueprint)

    assert len(received) == 1
    assert received[0]["blueprint_name"] == "event-test"
