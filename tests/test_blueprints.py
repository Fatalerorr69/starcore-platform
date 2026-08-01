"""
Blueprint Engine Tests
"""

from __future__ import annotations

import asyncio
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


async def test_executor_skips_dependent_after_dependency_fails():
    """ADR-010: depends_on is a success gate, not just an ordering
    constraint. BlueprintExecutor must never call provider.execute() for a
    resource whose declared dependency did not reach SUCCESS.
    """
    failing = FakeProvider(connect_result=False)
    failing.name = "failing"
    fake = FakeProvider(connect_result=True)
    registry.register(failing)
    registry.register(fake)

    blueprint = Blueprint(
        name="dependency-fail-test",
        resources=[
            ResourceSpec(name="a", provider="failing", kind="svc", config={}),
            ResourceSpec(name="b", provider="fake", kind="svc", config={}, depends_on=["a"]),
        ],
    )
    tasks = await BlueprintExecutor().execute(blueprint)

    by_resource = {t.resource: t for t in tasks}
    assert by_resource["a"].status == TaskStatus.FAILED
    assert by_resource["b"].status == TaskStatus.SKIPPED_DEPENDENCY_FAILED
    assert fake.executed == []


async def test_executor_skips_transitively_through_a_dependency_chain():
    """A depends on nothing and fails; B depends on A; C depends on B.
    Both B and C must be skipped -- SKIPPED_DEPENDENCY_FAILED must
    propagate transitively, not just one hop.
    """
    failing = FakeProvider(connect_result=False)
    failing.name = "failing"
    fake = FakeProvider(connect_result=True)
    registry.register(failing)
    registry.register(fake)

    blueprint = Blueprint(
        name="transitive-dependency-fail-test",
        resources=[
            ResourceSpec(name="a", provider="failing", kind="svc", config={}),
            ResourceSpec(name="b", provider="fake", kind="svc", config={}, depends_on=["a"]),
            ResourceSpec(name="c", provider="fake", kind="svc", config={}, depends_on=["b"]),
        ],
    )
    tasks = await BlueprintExecutor().execute(blueprint)

    by_resource = {t.resource: t for t in tasks}
    assert by_resource["a"].status == TaskStatus.FAILED
    assert by_resource["b"].status == TaskStatus.SKIPPED_DEPENDENCY_FAILED
    assert by_resource["c"].status == TaskStatus.SKIPPED_DEPENDENCY_FAILED
    assert fake.executed == []


async def test_executor_runs_dependent_when_dependency_succeeds():
    """Sanity check for the ADR-010 gate: a dependent must still run
    normally when its dependency actually succeeds.
    """
    fake = FakeProvider(connect_result=True)
    registry.register(fake)

    blueprint = Blueprint(
        name="dependency-success-test",
        resources=[
            ResourceSpec(name="a", provider="fake", kind="svc", config={}),
            ResourceSpec(name="b", provider="fake", kind="svc", config={}, depends_on=["a"]),
        ],
    )
    tasks = await BlueprintExecutor().execute(blueprint)

    by_resource = {t.resource: t for t in tasks}
    assert by_resource["a"].status == TaskStatus.SUCCESS
    assert by_resource["b"].status == TaskStatus.SUCCESS
    assert fake.executed == ["a", "b"]


async def test_executor_skips_dependent_when_dependency_itself_skipped_for_unknown_provider():
    """A dependency that is SKIPPED (unknown provider) must also block its
    dependent -- SKIPPED_DEPENDENCY_FAILED gates on "not SUCCESS", not
    specifically on FAILED.
    """
    fake = FakeProvider(connect_result=True)
    registry.register(fake)

    blueprint = Blueprint(
        name="dependency-unknown-provider-test",
        resources=[
            ResourceSpec(name="a", provider="does-not-exist", kind="svc", config={}),
            ResourceSpec(name="b", provider="fake", kind="svc", config={}, depends_on=["a"]),
        ],
    )
    tasks = await BlueprintExecutor().execute(blueprint)

    by_resource = {t.resource: t for t in tasks}
    assert by_resource["a"].status == TaskStatus.SKIPPED
    assert by_resource["b"].status == TaskStatus.SKIPPED_DEPENDENCY_FAILED
    assert fake.executed == []


async def test_executor_skips_convergence_point_of_diamond_when_one_branch_fails():
    """Diamond graph: base -> {left, right} -> tip. `left` fails; `right`
    succeeds. `tip` depends on both, so it must be skipped even though one
    of its two dependencies succeeded -- a dependent needs ALL declared
    dependencies to succeed, not just one.
    """
    failing = FakeProvider(connect_result=False)
    failing.name = "failing"
    fake = FakeProvider(connect_result=True)
    registry.register(failing)
    registry.register(fake)

    blueprint = Blueprint(
        name="diamond-partial-failure-test",
        resources=[
            ResourceSpec(name="base", provider="fake", kind="svc", config={}),
            ResourceSpec(
                name="left", provider="failing", kind="svc", config={}, depends_on=["base"]
            ),
            ResourceSpec(name="right", provider="fake", kind="svc", config={}, depends_on=["base"]),
            ResourceSpec(
                name="tip", provider="fake", kind="svc", config={}, depends_on=["left", "right"]
            ),
        ],
    )
    tasks = await BlueprintExecutor().execute(blueprint)

    by_resource = {t.resource: t for t in tasks}
    assert by_resource["base"].status == TaskStatus.SUCCESS
    assert by_resource["left"].status == TaskStatus.FAILED
    assert by_resource["right"].status == TaskStatus.SUCCESS
    assert by_resource["tip"].status == TaskStatus.SKIPPED_DEPENDENCY_FAILED
    assert fake.executed == ["base", "right"]


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


async def test_executor_marks_task_failed_when_execute_raises():
    """Lines 70-72: exception from provider.execute() is caught and task marked FAILED."""

    class _RaisingProvider(BaseProvider):
        name = "fake"

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

    blueprint = Blueprint(
        name="raise-test",
        resources=[ResourceSpec(name="thing", provider="fake", kind="svc", config={})],
    )
    tasks = await BlueprintExecutor().execute(blueprint)

    assert len(tasks) == 1
    assert tasks[0].status == TaskStatus.FAILED


# ---------------------------------------------------------------------------
# timeout_seconds — schema, planner, executor
# ---------------------------------------------------------------------------


def test_resource_spec_stores_timeout_seconds():
    spec = ResourceSpec(name="r", provider="p", kind="k", timeout_seconds=30)
    assert spec.timeout_seconds == 30.0


def test_resource_spec_timeout_seconds_defaults_to_none():
    spec = ResourceSpec(name="r", provider="p", kind="k")
    assert spec.timeout_seconds is None


def test_planner_create_plan_carries_timeout_seconds():
    blueprint = Blueprint(
        name="t",
        resources=[ResourceSpec(name="r", provider="p", kind="k", timeout_seconds=60)],
    )
    step = ExecutionPlanner().create_plan(blueprint)[0]
    assert step["timeout_seconds"] == 60.0


def test_planner_create_plan_carries_none_timeout():
    blueprint = Blueprint(
        name="t",
        resources=[ResourceSpec(name="r", provider="p", kind="k")],
    )
    step = ExecutionPlanner().create_plan(blueprint)[0]
    assert step["timeout_seconds"] is None


def test_planner_create_graph_carries_timeout_seconds():
    blueprint = Blueprint(
        name="t",
        resources=[ResourceSpec(name="r", provider="p", kind="k", timeout_seconds=45)],
    )
    tasks = list(ExecutionPlanner().create_graph(blueprint).all())
    assert tasks[0].timeout_seconds == 45.0


async def test_executor_succeeds_when_task_completes_before_timeout():
    fake = FakeProvider(connect_result=True)
    registry.register(fake)

    blueprint = Blueprint(
        name="timeout-ok",
        resources=[ResourceSpec(name="r", provider="fake", kind="k", timeout_seconds=10.0)],
    )
    tasks = await BlueprintExecutor().execute(blueprint)
    assert tasks[0].status == TaskStatus.SUCCESS


async def test_executor_marks_failed_when_timeout_exceeded():
    class _SlowProvider(BaseProvider):
        name = "slow"

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

    blueprint = Blueprint(
        name="timeout-fail",
        resources=[ResourceSpec(name="r", provider="slow", kind="k", timeout_seconds=0.01)],
    )
    tasks = await BlueprintExecutor().execute(blueprint)
    assert tasks[0].status == TaskStatus.FAILED


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
