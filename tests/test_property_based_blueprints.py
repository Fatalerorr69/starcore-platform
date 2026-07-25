"""
Property-Based Tests — Blueprints

Verifies structural invariants for Blueprint/ResourceSpec models,
ExecutionPlanner (create_graph + error handling), and BlueprintLoader
that must hold for all valid (and selected invalid) inputs.
"""

from __future__ import annotations

import pytest
import yaml
from blueprints.loader import BlueprintLoader
from blueprints.models import Blueprint, ResourceSpec
from blueprints.planner import ExecutionPlanner
from hypothesis import given
from hypothesis import strategies as st

# ── Shared strategies ──────────────────────────────────────────────────────────

_NAME = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz-",
    min_size=1,
    max_size=16,
)
_PROVIDER = st.sampled_from(["docker", "proxmox", "fake", "custom"])
_KIND = st.sampled_from(["vm", "lxc", "container", "svc"])
_VERSION = st.text(alphabet="0123456789.", min_size=1, max_size=10)


@st.composite
def valid_dag_blueprint(draw: st.DrawFn) -> Blueprint:
    """Generate a Blueprint whose dependency graph is a valid DAG."""
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
        provider = draw(_PROVIDER)
        kind = draw(_KIND)
        resources.append(
            ResourceSpec(name=name, provider=provider, kind=kind, config={}, depends_on=deps)
        )
    shuffled = draw(st.permutations(resources))
    return Blueprint(name="prop-test", resources=list(shuffled))


@st.composite
def cyclic_blueprint(draw: st.DrawFn) -> Blueprint:
    """Generate a Blueprint with a guaranteed two-node cycle: A → B → A."""
    a, b = draw(
        st.lists(
            st.text(min_size=1, max_size=8, alphabet="abcdefghijklmnopqrstuvwxyz"),
            min_size=2,
            max_size=2,
            unique=True,
        )
    )
    return Blueprint(
        name="cyclic",
        resources=[
            ResourceSpec(name=a, provider="fake", kind="svc", config={}, depends_on=[b]),
            ResourceSpec(name=b, provider="fake", kind="svc", config={}, depends_on=[a]),
        ],
    )


# ── Blueprint / ResourceSpec model properties ──────────────────────────────────


@given(blueprint=valid_dag_blueprint())
def test_blueprint_round_trips_through_model_dump_validate(blueprint: Blueprint) -> None:
    """model_validate(model_dump(bp)) produces an equal blueprint for all valid inputs."""
    restored = Blueprint.model_validate(blueprint.model_dump())
    assert restored == blueprint


@given(
    name=_NAME,
    provider=_PROVIDER,
    kind=_KIND,
    config=st.fixed_dictionaries({}),
)
def test_resource_spec_round_trips_through_model_dump_validate(
    name: str, provider: str, kind: str, config: dict
) -> None:
    """ResourceSpec survives model_dump/model_validate without data loss."""
    spec = ResourceSpec(name=name, provider=provider, kind=kind, config=config)
    restored = ResourceSpec.model_validate(spec.model_dump())
    assert restored == spec


@given(
    name=_NAME,
    version=_VERSION,
)
def test_blueprint_version_defaults_to_one_point_zero_when_omitted(name: str, version: str) -> None:
    """Blueprint.version defaults to '1.0' when not explicitly provided."""
    bp_default = Blueprint(name=name)
    assert bp_default.version == "1.0"

    bp_explicit = Blueprint(name=name, version=version)
    assert bp_explicit.version == version


@given(blueprint=valid_dag_blueprint())
def test_blueprint_resource_names_survive_round_trip(blueprint: Blueprint) -> None:
    """Resource name order is preserved through model_dump/model_validate."""
    names_before = [r.name for r in blueprint.resources]
    restored = Blueprint.model_validate(blueprint.model_dump())
    assert [r.name for r in restored.resources] == names_before


# ── ExecutionPlanner.create_graph properties ───────────────────────────────────


@given(blueprint=valid_dag_blueprint())
def test_planner_graph_task_ids_equal_resource_names(blueprint: Blueprint) -> None:
    """Every task produced by create_graph() has id equal to its resource name."""
    graph = ExecutionPlanner().create_graph(blueprint)
    for task in graph.all():
        assert task.id == task.resource


@given(blueprint=valid_dag_blueprint())
def test_planner_graph_task_payloads_equal_resource_config(blueprint: Blueprint) -> None:
    """Task payload in create_graph() equals the corresponding resource config."""
    by_name = {r.name: r for r in blueprint.resources}
    graph = ExecutionPlanner().create_graph(blueprint)
    for task in graph.all():
        assert task.payload == by_name[task.resource].config


@given(blueprint=valid_dag_blueprint())
def test_planner_graph_task_kinds_equal_resource_kinds(blueprint: Blueprint) -> None:
    """Task kind in create_graph() matches the corresponding resource kind."""
    by_name = {r.name: r for r in blueprint.resources}
    graph = ExecutionPlanner().create_graph(blueprint)
    for task in graph.all():
        assert task.kind == by_name[task.resource].kind


@given(blueprint=valid_dag_blueprint())
def test_planner_graph_and_plan_dependency_sets_agree(blueprint: Blueprint) -> None:
    """depends_on sets are identical between create_graph() tasks and blueprint resources."""
    by_name = {r.name: r for r in blueprint.resources}
    graph = ExecutionPlanner().create_graph(blueprint)
    for task in graph.all():
        assert set(task.depends_on) == set(by_name[task.resource].depends_on)


# ── ExecutionPlanner error-handling properties ─────────────────────────────────


@given(
    name=st.text(min_size=1, max_size=8, alphabet="abcdefghijklmnopqrstuvwxyz"),
)
def test_planner_raises_value_error_for_unknown_dependency(name: str) -> None:
    """create_plan() raises ValueError when a resource depends on an undeclared name."""
    blueprint = Blueprint(
        name="bad",
        resources=[
            ResourceSpec(
                name=name, provider="fake", kind="svc", config={}, depends_on=["__phantom__"]
            )
        ],
    )
    with pytest.raises(ValueError, match="unknown resource"):
        ExecutionPlanner().create_plan(blueprint)


@given(blueprint=cyclic_blueprint())
def test_planner_raises_value_error_for_cyclic_dependency(blueprint: Blueprint) -> None:
    """create_plan() raises ValueError for any blueprint whose deps form a cycle."""
    with pytest.raises(ValueError, match="circular dependency"):
        ExecutionPlanner().create_plan(blueprint)


@given(
    name=st.text(min_size=1, max_size=8, alphabet="abcdefghijklmnopqrstuvwxyz"),
)
def test_planner_create_graph_raises_for_unknown_dependency(name: str) -> None:
    """create_graph() raises ValueError for the same unknown-dep blueprints as create_plan()."""
    blueprint = Blueprint(
        name="bad",
        resources=[
            ResourceSpec(
                name=name, provider="fake", kind="svc", config={}, depends_on=["__phantom__"]
            )
        ],
    )
    with pytest.raises(ValueError, match="unknown resource"):
        ExecutionPlanner().create_graph(blueprint)


# ── BlueprintLoader properties ─────────────────────────────────────────────────


@given(blueprint=valid_dag_blueprint())
def test_loader_load_from_string_round_trips_valid_blueprint(blueprint: Blueprint) -> None:
    """load_from_string(yaml.dump(bp.model_dump())) produces an equal blueprint."""
    yaml_text = yaml.dump(blueprint.model_dump())
    loaded = BlueprintLoader.load_from_string(yaml_text)
    assert loaded == blueprint


@given(name=_NAME, version=_VERSION)
def test_loader_preserves_name_and_version(name: str, version: str) -> None:
    """load_from_string preserves blueprint name and version for all valid inputs."""
    bp = Blueprint(name=name, version=version)
    yaml_text = yaml.dump(bp.model_dump())
    loaded = BlueprintLoader.load_from_string(yaml_text)
    assert loaded.name == name
    assert loaded.version == version
