"""
Blueprint Engine Tests
"""

from pathlib import Path

from blueprints.executor import BlueprintExecutor
from blueprints.loader import BlueprintLoader
from blueprints.planner import ExecutionPlanner
from orchestrator.task import TaskStatus

EXAMPLE_PATH = Path(__file__).parent.parent / "packages" / "blueprints" / "examples" / "basic.yaml"


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


async def test_executor_runs_blueprint_end_to_end():
    blueprint = BlueprintLoader.load(EXAMPLE_PATH)
    tasks = await BlueprintExecutor().execute(blueprint)

    assert len(tasks) == 2
    for task in tasks:
        assert task.status in (TaskStatus.SUCCESS, TaskStatus.SKIPPED)


async def test_executor_skips_unknown_provider():
    from blueprints.models import Blueprint, ResourceSpec

    blueprint = Blueprint(
        name="unknown-provider-test",
        resources=[
            ResourceSpec(name="ghost", provider="does-not-exist", kind="vm", config={}),
        ],
    )
    tasks = await BlueprintExecutor().execute(blueprint)

    assert len(tasks) == 1
    assert tasks[0].status == TaskStatus.SKIPPED
