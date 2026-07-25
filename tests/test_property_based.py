"""
Property-Based Tests (Hypothesis)

Verifies structural invariants that hold for ALL valid inputs, not just
the specific examples covered by unit tests.
"""

from __future__ import annotations

from blueprints.models import Blueprint, ResourceSpec
from blueprints.planner import ExecutionPlanner
from hypothesis import given, settings
from hypothesis import strategies as st
from orchestrator.task import Task
from orchestrator.task_graph import TaskGraph

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
    resources = [
        ResourceSpec(name=n, provider="fake", kind="svc", config={}) for n in names
    ]
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
    tasks = {
        tid: Task(id=tid, provider="fake", action="create", resource=tid)
        for tid in task_ids
    }
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
