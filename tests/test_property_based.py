"""
Property-Based Tests (Hypothesis)

Verifies structural invariants that hold for ALL valid inputs, not just
the specific examples covered by unit tests.
"""

from __future__ import annotations

import asyncio
from unittest.mock import patch

from blueprints.models import Blueprint, ResourceSpec
from blueprints.planner import ExecutionPlanner
from hypothesis import given, settings
from hypothesis import strategies as st
from orchestrator.scheduler import Scheduler
from orchestrator.task import Task, TaskStatus
from orchestrator.task_graph import TaskGraph
from provider_sdk.base import BaseProvider
from provider_sdk.registry import registry

# ── Strategies ─────────────────────────────────────────────────────────────────

_RESOURCE_NAME = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz-",
    min_size=1,
    max_size=16,
)


@st.composite
def valid_dag_blueprint(draw: st.DrawFn) -> Blueprint:
    """Generate a Blueprint whose dependency graph is a valid DAG.

    Resources are numbered r0..r(n-1). Each resource may only depend on
    resources with a lower index, which guarantees the graph is acyclic and
    all dependency names exist. The list is then shuffled so the planner
    cannot rely on declaration order to satisfy dependencies.
    """
    n = draw(st.integers(min_value=1, max_value=8))
    names = [f"r{i}" for i in range(n)]

    resources: list[ResourceSpec] = []
    for i, name in enumerate(names):
        earlier = names[:i]
        deps = (
            draw(st.lists(st.sampled_from(earlier), max_size=min(i, 3), unique=True))
            if earlier
            else []
        )
        resources.append(
            ResourceSpec(name=name, provider="fake", kind="svc", config={}, depends_on=deps)
        )

    shuffled = draw(st.permutations(resources))
    return Blueprint(name="prop-test", resources=list(shuffled))


# ── ExecutionPlanner properties ────────────────────────────────────────────────


@given(blueprint=valid_dag_blueprint())
def test_planner_plan_respects_all_dependency_edges(blueprint: Blueprint) -> None:
    """For every declared edge (dep → resource), dep must appear before resource."""
    plan = ExecutionPlanner().create_plan(blueprint)
    position = {step["resource"]: idx for idx, step in enumerate(plan)}

    for resource in blueprint.resources:
        for dep in resource.depends_on:
            assert position[dep] < position[resource.name], (
                f"Violation: '{dep}' (pos {position[dep]}) appears after "
                f"'{resource.name}' (pos {position[resource.name]}) in {list(position)}"
            )


@given(blueprint=valid_dag_blueprint())
def test_planner_plan_contains_every_resource_exactly_once(blueprint: Blueprint) -> None:
    """The plan is a permutation of the blueprint's resource list."""
    plan = ExecutionPlanner().create_plan(blueprint)
    plan_names = [step["resource"] for step in plan]
    declared_names = sorted(r.name for r in blueprint.resources)

    assert sorted(plan_names) == declared_names
    assert len(plan_names) == len(set(plan_names))


@given(blueprint=valid_dag_blueprint())
def test_planner_graph_and_plan_have_equal_resource_counts(blueprint: Blueprint) -> None:
    """create_graph() and create_plan() always produce the same number of nodes."""
    plan = ExecutionPlanner().create_plan(blueprint)
    graph = ExecutionPlanner().create_graph(blueprint)

    assert len(plan) == len(list(graph.all()))


@given(
    names=st.lists(_RESOURCE_NAME, min_size=1, max_size=8, unique=True),
)
def test_planner_no_deps_preserves_declaration_order(names: list[str]) -> None:
    """A blueprint with no depends_on edges preserves the original declaration order."""
    resources = [ResourceSpec(name=n, provider="fake", kind="svc", config={}) for n in names]
    blueprint = Blueprint(name="order-test", resources=resources)
    plan = ExecutionPlanner().create_plan(blueprint)

    assert [step["resource"] for step in plan] == names


@given(blueprint=valid_dag_blueprint())
def test_planner_plan_steps_carry_provider_kind_config(blueprint: Blueprint) -> None:
    """Every plan step preserves the provider, kind, and config from the blueprint."""
    plan = ExecutionPlanner().create_plan(blueprint)
    by_name = {r.name: r for r in blueprint.resources}

    for step in plan:
        spec = by_name[step["resource"]]
        assert step["provider"] == spec.provider
        assert step["kind"] == spec.kind
        assert step["config"] == spec.config


# ── _strip_code_fences properties ─────────────────────────────────────────────


@given(st.text())
@settings(max_examples=500)
def test_strip_code_fences_is_idempotent(text: str) -> None:
    """strip(strip(x)) == strip(x) for all inputs."""
    from ai.generator import _strip_code_fences

    once = _strip_code_fences(text)
    assert _strip_code_fences(once) == once


@given(
    inner=st.text(
        alphabet=st.characters(blacklist_characters="`"),
        max_size=200,
    )
)
def test_strip_code_fences_unwraps_yaml_fence(inner: str) -> None:
    """```yaml\\n<content>\\n``` unwraps to content.strip() when content has no backticks."""
    from ai.generator import _strip_code_fences

    assert _strip_code_fences(f"```yaml\n{inner}\n```") == inner.strip()


@given(
    inner=st.text(
        alphabet=st.characters(blacklist_characters="`"),
        max_size=200,
    )
)
def test_strip_code_fences_unwraps_plain_fence(inner: str) -> None:
    """Plain ``` fences (no language tag) are also removed."""
    from ai.generator import _strip_code_fences

    assert _strip_code_fences(f"```\n{inner}\n```") == inner.strip()


@given(
    text=st.text(
        alphabet=st.characters(blacklist_characters="`"),
        max_size=300,
    )
)
def test_strip_code_fences_is_noop_on_text_without_backticks(text: str) -> None:
    """Text containing no backticks is returned unchanged (after whitespace stripping)."""
    from ai.generator import _strip_code_fences

    assert _strip_code_fences(text) == text.strip()


# ── TaskGraph properties ───────────────────────────────────────────────────────


@given(
    task_ids=st.lists(
        st.text(min_size=1, max_size=12, alphabet="abcdefghijklmnopqrstuvwxyz"),
        min_size=1,
        max_size=12,
        unique=True,
    )
)
def test_task_graph_get_returns_same_task_after_add(task_ids: list[str]) -> None:
    """graph.get(id) always returns the exact Task object that was added."""
    graph = TaskGraph()
    tasks = {tid: Task(id=tid, provider="fake", action="create", resource=tid) for tid in task_ids}
    for task in tasks.values():
        graph.add_task(task)

    for tid, original_task in tasks.items():
        assert graph.get(tid) is original_task


@given(
    n=st.integers(min_value=2, max_value=10),
)
def test_task_graph_dependents_consistent_with_depends_on(n: int) -> None:
    """If task B declares depends_on=[A], then A must appear in dependents_of(A)."""
    ids = [f"t{i}" for i in range(n)]
    graph = TaskGraph()

    # Linear chain: t0 ← t1 ← t2 ← … ← t(n-1)
    for i, tid in enumerate(ids):
        deps = [ids[i - 1]] if i > 0 else []
        graph.add_task(
            Task(id=tid, provider="fake", action="create", resource=tid, depends_on=deps)
        )

    for i in range(n - 1):
        assert ids[i + 1] in graph.dependents_of(ids[i])


@given(
    task_ids=st.lists(
        st.text(min_size=1, max_size=12, alphabet="abcdefghijklmnopqrstuvwxyz"),
        min_size=1,
        max_size=12,
        unique=True,
    )
)
def test_task_graph_all_returns_every_added_task(task_ids: list[str]) -> None:
    """graph.all() returns every task that was added, no more and no fewer."""
    graph = TaskGraph()
    for tid in task_ids:
        graph.add_task(Task(id=tid, provider="fake", action="create", resource=tid))

    returned_ids = {task.id for task in graph.all()}
    assert returned_ids == set(task_ids)


# ── Blueprint model properties ─────────────────────────────────────────────────


@given(
    name=_RESOURCE_NAME,
    provider=st.sampled_from(["docker", "proxmox", "custom"]),
    kind=st.sampled_from(["container", "vm", "lxc", "svc"]),
)
def test_resource_spec_always_has_empty_depends_on_by_default(
    name: str, provider: str, kind: str
) -> None:
    """ResourceSpec.depends_on defaults to an empty list for all valid inputs."""
    spec = ResourceSpec(name=name, provider=provider, kind=kind, config={})
    assert spec.depends_on == []


@given(
    name=_RESOURCE_NAME,
    version=st.text(min_size=1, max_size=10, alphabet="0123456789."),
)
def test_blueprint_resources_default_to_empty_list(name: str, version: str) -> None:
    """Blueprint.resources defaults to [] when not provided."""
    bp = Blueprint(name=name, version=version)
    assert bp.resources == []
    assert bp.name == name
    assert bp.version == version


# ── Orchestrator: supporting fixtures ─────────────────────────────────────────

_TASK_ID = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz",
    min_size=1,
    max_size=12,
)


@st.composite
def valid_dag_task_graph(draw: st.DrawFn, provider: str = "fake") -> TaskGraph:
    """Generate a TaskGraph whose dependency graph is a valid DAG.

    Same construction as valid_dag_blueprint but produces a TaskGraph directly.
    """
    n = draw(st.integers(min_value=1, max_value=8))
    ids = [f"t{i}" for i in range(n)]
    graph = TaskGraph()
    for i, tid in enumerate(ids):
        earlier = ids[:i]
        deps = (
            draw(st.lists(st.sampled_from(earlier), max_size=min(i, 3), unique=True))
            if earlier
            else []
        )
        graph.add_task(
            Task(id=tid, provider=provider, action="create", resource=tid, depends_on=deps)
        )
    return graph


class _SucceedingProvider(BaseProvider):
    name = "succeeder"

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> None:
        return None

    async def health(self) -> dict:
        return {"status": "ok", "provider": self.name}

    async def list_resources(self) -> list[dict]:
        return []

    async def execute(self, task) -> None:
        return None


_TERMINAL_STATUSES = {TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.SKIPPED}


# ── Additional TaskGraph properties ───────────────────────────────────────────


@given(
    task_ids=st.lists(_TASK_ID, min_size=1, max_size=12, unique=True),
)
def test_task_graph_dependents_of_missing_id_returns_empty_set(
    task_ids: list[str],
) -> None:
    """dependents_of() returns an empty set for an ID that was never added."""
    graph = TaskGraph()
    for tid in task_ids:
        graph.add_task(Task(id=tid, provider="fake", action="create", resource=tid))

    assert graph.dependents_of("__no_such_task__") == set()


@given(
    ids=st.lists(_TASK_ID, min_size=1, max_size=8, unique=True),
)
def test_task_graph_duplicate_id_overwrites_previous_task(ids: list[str]) -> None:
    """Adding a task with an already-registered ID replaces the previous entry."""
    graph = TaskGraph()
    for tid in ids:
        graph.add_task(Task(id=tid, provider="first", action="create", resource=tid))

    new_tasks: dict[str, Task] = {}
    for tid in ids:
        replacement = Task(id=tid, provider="second", action="delete", resource=tid)
        graph.add_task(replacement)
        new_tasks[tid] = replacement

    for tid in ids:
        assert graph.get(tid) is new_tasks[tid]
    assert len(list(graph.all())) == len(ids)


@given(n=st.integers(min_value=1, max_value=10))
def test_task_graph_leaf_node_has_no_dependents(n: int) -> None:
    """In a linear chain the last (leaf) task has no registered dependents."""
    ids = [f"t{i}" for i in range(n)]
    graph = TaskGraph()
    for i, tid in enumerate(ids):
        deps = [ids[i - 1]] if i > 0 else []
        graph.add_task(
            Task(id=tid, provider="fake", action="create", resource=tid, depends_on=deps)
        )

    assert graph.dependents_of(ids[-1]) == set()


@given(graph=valid_dag_task_graph())
def test_task_graph_total_edges_equals_total_dependency_declarations(
    graph: TaskGraph,
) -> None:
    """Sum of all edge-set sizes equals the total number of depends_on entries across all tasks."""
    declared = sum(len(t.depends_on) for t in graph.all())
    stored = sum(len(s) for s in graph.edges.values())
    assert stored == declared


# ── Task model properties ──────────────────────────────────────────────────────


@given(
    tid=_TASK_ID,
    provider=st.sampled_from(["docker", "proxmox", "fake"]),
    action=st.sampled_from(["create", "delete", "start", "stop"]),
    resource=_TASK_ID,
)
def test_task_default_status_is_always_pending(
    tid: str, provider: str, action: str, resource: str
) -> None:
    """A newly created Task always starts with PENDING status regardless of other fields."""
    task = Task(id=tid, provider=provider, action=action, resource=resource)
    assert task.status == TaskStatus.PENDING


@given(
    tid=_TASK_ID,
    provider=st.sampled_from(["docker", "proxmox", "fake"]),
    action=st.sampled_from(["create", "delete", "start", "stop"]),
    resource=_TASK_ID,
)
def test_task_optional_fields_default_correctly(
    tid: str, provider: str, action: str, resource: str
) -> None:
    """payload, result, depends_on, and kind all default to their zero values."""
    task = Task(id=tid, provider=provider, action=action, resource=resource)
    assert task.payload == {}
    assert task.result == {}
    assert task.depends_on == []
    assert task.kind == ""


# ── Scheduler properties ───────────────────────────────────────────────────────


@given(
    task_ids=st.lists(_TASK_ID, min_size=1, max_size=6, unique=True),
)
def test_scheduler_returns_same_number_of_tasks_as_graph(task_ids: list[str]) -> None:
    """Scheduler.execute() returns exactly as many Task objects as the graph contains."""
    graph = TaskGraph()
    for tid in task_ids:
        graph.add_task(Task(id=tid, provider="ghost-xyz", action="create", resource=tid))

    registry._providers.clear()
    try:
        with patch("orchestrator.scheduler.register_default_providers"):
            tasks = asyncio.run(Scheduler().execute(graph))
    finally:
        registry._providers.clear()

    assert len(tasks) == len(task_ids)


@given(
    task_ids=st.lists(_TASK_ID, min_size=1, max_size=6, unique=True),
)
def test_scheduler_unregistered_provider_marks_all_tasks_skipped(
    task_ids: list[str],
) -> None:
    """Tasks whose provider is absent from the registry are marked SKIPPED."""
    graph = TaskGraph()
    for tid in task_ids:
        graph.add_task(Task(id=tid, provider="ghost-xyz", action="create", resource=tid))

    registry._providers.clear()
    try:
        with patch("orchestrator.scheduler.register_default_providers"):
            tasks = asyncio.run(Scheduler().execute(graph))
    finally:
        registry._providers.clear()

    for task in tasks:
        assert task.status == TaskStatus.SKIPPED


@given(n=st.integers(min_value=1, max_value=6))
def test_scheduler_stalled_graph_marks_all_tasks_failed(n: int) -> None:
    """A graph where every task depends on a non-existent ID stalls: all tasks reach FAILED."""
    graph = TaskGraph()
    for i in range(n):
        graph.add_task(
            Task(
                id=f"t{i}",
                provider="ghost-xyz",
                action="create",
                resource=f"r{i}",
                depends_on=["__phantom__"],
            )
        )

    registry._providers.clear()
    try:
        with patch("orchestrator.scheduler.register_default_providers"):
            tasks = asyncio.run(Scheduler().execute(graph))
    finally:
        registry._providers.clear()

    assert all(t.status == TaskStatus.FAILED for t in tasks)


@given(graph=valid_dag_task_graph(provider="succeeder"))
def test_scheduler_all_tasks_succeed_with_working_provider(graph: TaskGraph) -> None:
    """Every task in a valid DAG reaches SUCCESS when the provider connects and executes cleanly."""
    registry._providers.clear()
    registry.register(_SucceedingProvider())
    try:
        with patch("orchestrator.scheduler.register_default_providers"):
            tasks = asyncio.run(Scheduler().execute(graph))
    finally:
        registry._providers.clear()

    for task in tasks:
        assert task.status == TaskStatus.SUCCESS


@given(graph=valid_dag_task_graph(provider="ghost-xyz"))
def test_scheduler_all_tasks_reach_terminal_status(graph: TaskGraph) -> None:
    """After execution no task remains in a non-terminal state (PENDING or RUNNING)."""
    registry._providers.clear()
    try:
        with patch("orchestrator.scheduler.register_default_providers"):
            tasks = asyncio.run(Scheduler().execute(graph))
    finally:
        registry._providers.clear()

    for task in tasks:
        assert task.status in _TERMINAL_STATUSES
