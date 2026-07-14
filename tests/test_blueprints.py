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
