"""
Execution Planner
"""

from __future__ import annotations

from orchestrator.task import Task
from orchestrator.task_graph import TaskGraph

from .models import Blueprint


class ExecutionPlanner:
    def create_plan(self, blueprint: Blueprint):
        return [
            {
                "provider": resource.provider,
                "resource": resource.name,
                "kind": resource.kind,
                "config": resource.config,
            }
            for resource in blueprint.resources
        ]

    def create_graph(self, blueprint: Blueprint) -> TaskGraph:
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
