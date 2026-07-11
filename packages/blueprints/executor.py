"""
Blueprint Executor
"""

from provider_sdk.registry import registry

from .planner import ExecutionPlanner


class BlueprintExecutor:
    async def execute(self, blueprint):
        planner = ExecutionPlanner()

        plan = planner.create_plan(blueprint)

        for step in plan:
            provider = registry.get(step["provider"])

            await provider.connect()

            # Další implementace:
            # await provider.create(step)
