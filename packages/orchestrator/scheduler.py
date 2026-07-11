"""
Scheduler
"""

from provider_sdk.registry import registry

from .task import TaskStatus


class Scheduler:
    async def execute(self, graph):
        for task in graph.all():
            provider = registry.get(task.provider)

            task.status = TaskStatus.RUNNING

            try:
                await provider.execute(task)

                task.status = TaskStatus.SUCCESS

            except Exception:
                task.status = TaskStatus.FAILED

                raise
