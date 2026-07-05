"""
Execution Planner
"""

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
