"""
Property-Based Tests — ADR-010 Dependency Failure Semantics

Verifies the success-gate invariant across all valid DAG structures and both
execution paths (sequential BlueprintExecutor, concurrent Scheduler): a task
whose dependency finished FAILED, SKIPPED, or SKIPPED_DEPENDENCY_FAILED is
itself marked SKIPPED_DEPENDENCY_FAILED and never reaches provider.execute().
"""

from __future__ import annotations

import asyncio
from unittest.mock import patch

from blueprints.executor import BlueprintExecutor
from blueprints.models import Blueprint, ResourceSpec
from hypothesis import given
from hypothesis import strategies as st
from orchestrator.scheduler import Scheduler
from orchestrator.task import Task, TaskStatus
from orchestrator.task_graph import TaskGraph
from provider_sdk.base import BaseProvider
from provider_sdk.registry import registry

# ── Test providers ─────────────────────────────────────────────────────────────


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


class _FailingProvider(BaseProvider):
    """Provider whose connect() always returns False, causing tasks to reach FAILED."""

    name = "failer"

    async def connect(self) -> bool:
        return False

    async def disconnect(self) -> None:
        return None

    async def health(self) -> dict:
        return {"status": "fail", "provider": self.name}

    async def list_resources(self) -> list[dict]:
        return []

    async def execute(self, task) -> None:
        return None


class _TrackingProvider(BaseProvider):
    """Provider that records every execute() call for assertion."""

    name = "tracker"

    def __init__(self) -> None:
        self.executed_resources: list[str] = []

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> None:
        return None

    async def health(self) -> dict:
        return {"status": "ok", "provider": self.name}

    async def list_resources(self) -> list[dict]:
        return []

    async def execute(self, task) -> None:
        self.executed_resources.append(task.resource)


_NAME = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz",
    min_size=1,
    max_size=12,
)


# ── Scheduler (concurrent) path ────────────────────────────────────────────────


@given(name_a=_NAME, name_b=_NAME)
def test_scheduler_dependent_of_skipped_reaches_skipped_dependency_failed(
    name_a: str, name_b: str
) -> None:
    """Scheduler: B depends on A; A is SKIPPED (unregistered provider) → B must be
    SKIPPED_DEPENDENCY_FAILED, never SUCCESS or SKIPPED."""
    if name_a == name_b:
        name_b = name_b + "x"

    graph = TaskGraph()
    graph.add_task(Task(id=name_a, provider="ghost-xyz", action="create", resource=name_a))
    graph.add_task(
        Task(
            id=name_b,
            provider="succeeder",
            action="create",
            resource=name_b,
            depends_on=[name_a],
        )
    )

    registry._providers.clear()
    registry.register(_SucceedingProvider())
    try:
        with patch("orchestrator.scheduler.register_default_providers"):
            tasks = asyncio.run(Scheduler().execute(graph))
    finally:
        registry._providers.clear()

    by_id = {t.id: t for t in tasks}
    assert by_id[name_a].status == TaskStatus.SKIPPED
    assert by_id[name_b].status == TaskStatus.SKIPPED_DEPENDENCY_FAILED


@given(name_a=_NAME, name_b=_NAME)
def test_scheduler_dependent_of_failed_reaches_skipped_dependency_failed(
    name_a: str, name_b: str
) -> None:
    """Scheduler: B depends on A; A is FAILED (connect() returns False) → B must be
    SKIPPED_DEPENDENCY_FAILED."""
    if name_a == name_b:
        name_b = name_b + "x"

    graph = TaskGraph()
    graph.add_task(Task(id=name_a, provider="failer", action="create", resource=name_a))
    graph.add_task(
        Task(
            id=name_b,
            provider="succeeder",
            action="create",
            resource=name_b,
            depends_on=[name_a],
        )
    )

    registry._providers.clear()
    registry.register(_FailingProvider())
    registry.register(_SucceedingProvider())
    try:
        with patch("orchestrator.scheduler.register_default_providers"):
            tasks = asyncio.run(Scheduler().execute(graph))
    finally:
        registry._providers.clear()

    by_id = {t.id: t for t in tasks}
    assert by_id[name_a].status == TaskStatus.FAILED
    assert by_id[name_b].status == TaskStatus.SKIPPED_DEPENDENCY_FAILED


@given(n=st.integers(min_value=2, max_value=6))
def test_scheduler_chain_propagates_skipped_dependency_failed(n: int) -> None:
    """Scheduler: in a linear chain where the root is SKIPPED (unregistered provider),
    every downstream task reaches SKIPPED_DEPENDENCY_FAILED regardless of chain length."""
    ids = [f"t{i}" for i in range(n)]
    graph = TaskGraph()
    graph.add_task(Task(id=ids[0], provider="ghost-xyz", action="create", resource=ids[0]))
    for i in range(1, n):
        graph.add_task(
            Task(
                id=ids[i],
                provider="succeeder",
                action="create",
                resource=ids[i],
                depends_on=[ids[i - 1]],
            )
        )

    registry._providers.clear()
    registry.register(_SucceedingProvider())
    try:
        with patch("orchestrator.scheduler.register_default_providers"):
            tasks = asyncio.run(Scheduler().execute(graph))
    finally:
        registry._providers.clear()

    by_id = {t.id: t for t in tasks}
    assert by_id[ids[0]].status == TaskStatus.SKIPPED
    for tid in ids[1:]:
        assert by_id[tid].status == TaskStatus.SKIPPED_DEPENDENCY_FAILED


@given(names=st.lists(_NAME, min_size=3, max_size=3, unique=True))
def test_scheduler_independent_task_succeeds_despite_sibling_failure(
    names: list[str],
) -> None:
    """Scheduler: C has no dependencies and reaches SUCCESS even when A (root) is
    SKIPPED and B (depends on A) is SKIPPED_DEPENDENCY_FAILED."""
    name_a, name_b, name_c = names

    graph = TaskGraph()
    graph.add_task(Task(id=name_a, provider="ghost-xyz", action="create", resource=name_a))
    graph.add_task(
        Task(
            id=name_b,
            provider="succeeder",
            action="create",
            resource=name_b,
            depends_on=[name_a],
        )
    )
    graph.add_task(Task(id=name_c, provider="succeeder", action="create", resource=name_c))

    registry._providers.clear()
    registry.register(_SucceedingProvider())
    try:
        with patch("orchestrator.scheduler.register_default_providers"):
            tasks = asyncio.run(Scheduler().execute(graph))
    finally:
        registry._providers.clear()

    by_id = {t.id: t for t in tasks}
    assert by_id[name_a].status == TaskStatus.SKIPPED
    assert by_id[name_b].status == TaskStatus.SKIPPED_DEPENDENCY_FAILED
    assert by_id[name_c].status == TaskStatus.SUCCESS


@given(name_a=_NAME, name_b=_NAME)
def test_scheduler_execute_never_called_for_skipped_dependency_failed(
    name_a: str, name_b: str
) -> None:
    """Scheduler: provider.execute() is never invoked for a task that is
    SKIPPED_DEPENDENCY_FAILED — the gate stops execution before reaching the provider."""
    if name_a == name_b:
        name_b = name_b + "x"

    tracker = _TrackingProvider()

    graph = TaskGraph()
    graph.add_task(Task(id=name_a, provider="ghost-xyz", action="create", resource=name_a))
    graph.add_task(
        Task(
            id=name_b,
            provider="tracker",
            action="create",
            resource=name_b,
            depends_on=[name_a],
        )
    )

    registry._providers.clear()
    registry.register(tracker)
    try:
        with patch("orchestrator.scheduler.register_default_providers"):
            asyncio.run(Scheduler().execute(graph))
    finally:
        registry._providers.clear()

    assert name_b not in tracker.executed_resources


# ── BlueprintExecutor (sequential) path ────────────────────────────────────────


@given(name_a=_NAME, name_b=_NAME)
def test_executor_dependent_of_skipped_reaches_skipped_dependency_failed(
    name_a: str, name_b: str
) -> None:
    """BlueprintExecutor: B depends on A; A is SKIPPED (unregistered) → B must be
    SKIPPED_DEPENDENCY_FAILED, never SUCCESS or SKIPPED."""
    if name_a == name_b:
        name_b = name_b + "x"

    blueprint = Blueprint(
        name="dep-test",
        resources=[
            ResourceSpec(name=name_a, provider="ghost-xyz", kind="svc", config={}, depends_on=[]),
            ResourceSpec(
                name=name_b,
                provider="succeeder",
                kind="svc",
                config={},
                depends_on=[name_a],
            ),
        ],
    )

    registry._providers.clear()
    registry.register(_SucceedingProvider())
    try:
        with patch("blueprints.executor.register_default_providers"):
            tasks = asyncio.run(BlueprintExecutor().execute(blueprint))
    finally:
        registry._providers.clear()

    by_resource = {t.resource: t for t in tasks}
    assert by_resource[name_a].status == TaskStatus.SKIPPED
    assert by_resource[name_b].status == TaskStatus.SKIPPED_DEPENDENCY_FAILED


@given(n=st.integers(min_value=2, max_value=6))
def test_executor_chain_propagates_skipped_dependency_failed(n: int) -> None:
    """BlueprintExecutor: in a linear chain where the root is SKIPPED (unregistered
    provider), every downstream task reaches SKIPPED_DEPENDENCY_FAILED regardless of
    chain length."""
    names = [f"r{i}" for i in range(n)]
    resources = [
        ResourceSpec(name=names[0], provider="ghost-xyz", kind="svc", config={}, depends_on=[]),
        *[
            ResourceSpec(
                name=names[i],
                provider="succeeder",
                kind="svc",
                config={},
                depends_on=[names[i - 1]],
            )
            for i in range(1, n)
        ],
    ]

    blueprint = Blueprint(name="chain-test", resources=resources)

    registry._providers.clear()
    registry.register(_SucceedingProvider())
    try:
        with patch("blueprints.executor.register_default_providers"):
            tasks = asyncio.run(BlueprintExecutor().execute(blueprint))
    finally:
        registry._providers.clear()

    by_resource = {t.resource: t for t in tasks}
    assert by_resource[names[0]].status == TaskStatus.SKIPPED
    for name in names[1:]:
        assert by_resource[name].status == TaskStatus.SKIPPED_DEPENDENCY_FAILED


@given(name_a=_NAME, name_b=_NAME)
def test_executor_execute_never_called_for_skipped_dependency_failed(
    name_a: str, name_b: str
) -> None:
    """BlueprintExecutor: provider.execute() is never invoked for a task that is
    SKIPPED_DEPENDENCY_FAILED — the gate stops execution before reaching the provider."""
    if name_a == name_b:
        name_b = name_b + "x"

    tracker = _TrackingProvider()

    blueprint = Blueprint(
        name="no-execute-test",
        resources=[
            ResourceSpec(name=name_a, provider="ghost-xyz", kind="svc", config={}, depends_on=[]),
            ResourceSpec(
                name=name_b,
                provider="tracker",
                kind="svc",
                config={},
                depends_on=[name_a],
            ),
        ],
    )

    registry._providers.clear()
    registry.register(tracker)
    try:
        with patch("blueprints.executor.register_default_providers"):
            asyncio.run(BlueprintExecutor().execute(blueprint))
    finally:
        registry._providers.clear()

    assert name_b not in tracker.executed_resources
