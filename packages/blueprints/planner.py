"""
Execution Planner
"""

from __future__ import annotations

from collections import deque
from typing import Any

from orchestrator.task import Task
from orchestrator.task_graph import TaskGraph

from .models import Blueprint, ResourceSpec


class ExecutionPlanner:
    """Builds execution plans and dependency graphs from a :class:`Blueprint`.

    Two representations of the same blueprint are produced, consumed by the
    platform's two execution paths:

    - :meth:`create_plan` returns a flat, dependency-ordered list of
      resource-creation steps consumed by the sequential
      :class:`~blueprints.executor.BlueprintExecutor`.
    - :meth:`create_graph` returns a :class:`~orchestrator.task_graph.TaskGraph`
      consumed by the concurrent, wave-based
      :class:`~orchestrator.scheduler.Scheduler` (``--parallel``).

    Both representations honor every resource's declared ``depends_on``
    list. Neither path silently reorders resources in a way that would let a
    resource be created before a resource it depends on -- a blueprint's
    declared ``depends_on`` edges are treated as a binding constraint on
    execution order in both the sequential and the concurrent path.
    """

    def create_plan(self, blueprint: Blueprint) -> list[dict[str, Any]]:
        """Build a flat, dependency-ordered execution plan.

        The returned steps are ordered so that no resource precedes any
        resource it declares in ``depends_on``, regardless of the order in
        which resources were declared in the blueprint. When a blueprint
        declares no dependencies at all, the original declaration order is
        preserved unchanged.

        Args:
            blueprint: The blueprint to plan.

        Returns:
            A list of plan steps, each a mapping with ``provider``,
            ``resource``, ``kind``, and ``config`` keys, in a valid
            dependency-respecting execution order.

        Raises:
            ValueError: If any resource declares a dependency on a resource
                name that does not exist in the blueprint, or if the
                dependency declarations form a cycle.
        """
        ordered_resources = self._topological_order(blueprint.resources)
        return [
            {
                "provider": resource.provider,
                "resource": resource.name,
                "kind": resource.kind,
                "config": resource.config,
            }
            for resource in ordered_resources
        ]

    def create_graph(self, blueprint: Blueprint) -> TaskGraph:
        """Build a dependency graph consumed by the concurrent scheduler.

        Args:
            blueprint: The blueprint to plan.

        Returns:
            A :class:`~orchestrator.task_graph.TaskGraph` with one task per
            resource, wired up according to each resource's ``depends_on``.

        Raises:
            ValueError: If any resource declares a dependency on a resource
                name that does not exist in the blueprint.
        """
        names = {resource.name for resource in blueprint.resources}
        graph = TaskGraph()
        for resource in blueprint.resources:
            unknown = set(resource.depends_on) - names
            if unknown:
                raise ValueError(
                    f"Resource '{resource.name}' depends on unknown resource(s): "
                    f"{', '.join(sorted(unknown))}"
                )
            task = Task(
                id=resource.name,
                provider=resource.provider,
                action="create",
                resource=resource.name,
                payload=resource.config,
                depends_on=list(resource.depends_on),
                kind=resource.kind,
            )
            graph.add_task(task)
        return graph

    @staticmethod
    def _topological_order(resources: list[ResourceSpec]) -> list[ResourceSpec]:
        """Order resources so that every dependency precedes its dependents.

        Implements Kahn's algorithm with a FIFO ready-queue seeded in
        blueprint declaration order. Seeding the queue in declaration order
        guarantees that a blueprint with no ``depends_on`` edges at all is
        returned in its original declaration order, unchanged -- this keeps
        the method fully backward-compatible with blueprints that do not use
        dependencies.

        Args:
            resources: The resource specs to order, as declared in the
                blueprint.

        Returns:
            The same resource specs, reordered to respect every declared
            dependency.

        Raises:
            ValueError: If a resource depends on an unknown resource name,
                or if the dependency declarations form a cycle.
        """
        by_name: dict[str, ResourceSpec] = {resource.name: resource for resource in resources}

        for resource in resources:
            unknown = set(resource.depends_on) - by_name.keys()
            if unknown:
                raise ValueError(
                    f"Resource '{resource.name}' depends on unknown resource(s): "
                    f"{', '.join(sorted(unknown))}"
                )

        in_degree: dict[str, int] = {name: len(spec.depends_on) for name, spec in by_name.items()}
        dependents: dict[str, list[str]] = {name: [] for name in by_name}
        for resource in resources:
            for dependency_name in resource.depends_on:
                dependents[dependency_name].append(resource.name)

        ready: deque[str] = deque(
            resource.name for resource in resources if in_degree[resource.name] == 0
        )
        ordered_names: list[str] = []

        while ready:
            current = ready.popleft()
            ordered_names.append(current)
            for dependent_name in dependents[current]:
                in_degree[dependent_name] -= 1
                if in_degree[dependent_name] == 0:
                    ready.append(dependent_name)

        if len(ordered_names) != len(resources):
            unresolved = sorted(set(by_name) - set(ordered_names))
            raise ValueError(
                "Blueprint resources contain a circular dependency involving: "
                f"{', '.join(unresolved)}"
            )

        return [by_name[name] for name in ordered_names]
