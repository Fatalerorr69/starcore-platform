"""
Scheduler

Executes a TaskGraph respecting task dependencies (depends_on).
Tasks whose dependencies are already satisfied run concurrently,
unlike BlueprintExecutor which runs steps strictly sequentially.
"""

from __future__ import annotations

import asyncio

from loguru import logger
from provider_sdk.registry import register_default_providers, registry

from .task import Task, TaskStatus
from .task_graph import TaskGraph


class Scheduler:
    async def execute(self, graph: TaskGraph) -> list[Task]:
        register_default_providers()

        all_tasks = list(graph.all())
        completed: set[str] = set()
        dispatched: set[str] = set()
        used_providers: set[str] = set()

        while len(completed) < len(all_tasks):
            ready = [
                task
                for task in all_tasks
                if task.id not in dispatched and all(dep in completed for dep in task.depends_on)
            ]
            if not ready:
                remaining = [t for t in all_tasks if t.id not in completed]
                for task in remaining:
                    task.status = TaskStatus.FAILED
                logger.error(
                    "Scheduler stalled: {} task(s) have unresolved or cyclic dependencies",
                    len(remaining),
                )
                break

            dispatched.update(task.id for task in ready)
            await asyncio.gather(*(self._run_task(task, used_providers) for task in ready))
            completed.update(task.id for task in ready)

        for name in used_providers:
            await registry.get(name).disconnect()

        return all_tasks

    async def _run_task(self, task: Task, used_providers: set[str]) -> None:
        if task.provider not in registry.names():
            logger.warning(
                "Provider '{}' not registered, skipping resource '{}'",
                task.provider,
                task.resource,
            )
            task.status = TaskStatus.SKIPPED
            return

        task.status = TaskStatus.RUNNING
        try:
            provider = registry.get(task.provider)
            connected = await provider.connect()
            if not connected:
                logger.warning(
                    "Provider '{}' failed to connect, marking resource '{}' as failed",
                    task.provider,
                    task.resource,
                )
                task.status = TaskStatus.FAILED
                return
            used_providers.add(task.provider)
            await provider.execute(task)
            task.status = TaskStatus.SUCCESS
        except Exception:
            logger.exception("Failed to execute task for resource '{}'", task.resource)
            task.status = TaskStatus.FAILED
