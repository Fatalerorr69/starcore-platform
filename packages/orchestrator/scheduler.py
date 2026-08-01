"""
Scheduler

Executes a TaskGraph respecting task dependencies (depends_on).
Tasks whose dependencies are already satisfied run concurrently,
unlike BlueprintExecutor which runs steps strictly sequentially.

`depends_on` is a success gate, not just an ordering constraint (ADR-010):
a task is only dispatched to its provider once every task it depends on has
reached TaskStatus.SUCCESS. A dependency that finished FAILED, SKIPPED, or
SKIPPED_DEPENDENCY_FAILED causes every task that (transitively) depends on
it to be marked SKIPPED_DEPENDENCY_FAILED without ever calling
provider.execute(). See BlueprintExecutor for the identical contract on the
sequential path.
"""

from __future__ import annotations

import asyncio

from core.events import event_bus
from loguru import logger
from provider_sdk.registry import register_default_providers, registry

from .task import Task, TaskStatus
from .task_graph import TaskGraph
from .timeout import TaskTimeoutError, TimeoutConfig, execute_with_timeout


class Scheduler:
    async def execute(self, graph: TaskGraph) -> list[Task]:
        register_default_providers()

        all_tasks = list(graph.all())
        by_id = {task.id: task for task in all_tasks}
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

            # A task whose depends_on names a task that finished without
            # reaching SUCCESS (FAILED, SKIPPED, or itself
            # SKIPPED_DEPENDENCY_FAILED) must never reach provider.execute():
            # depends_on is a success gate, not just an ordering constraint.
            # Because `completed` includes SKIPPED_DEPENDENCY_FAILED tasks
            # too, this propagates transitively across multiple waves.
            runnable: list[Task] = []
            for task in ready:
                blocking = [
                    dep for dep in task.depends_on if by_id[dep].status != TaskStatus.SUCCESS
                ]
                if blocking:
                    await self._skip_dependency_failed(task, blocking)
                else:
                    runnable.append(task)

            await asyncio.gather(*(self._run_task(task, used_providers) for task in runnable))
            completed.update(task.id for task in ready)

        for name in used_providers:
            await registry.get(name).disconnect()

        await event_bus.emit(
            "run.completed",
            {
                "tasks": [
                    {
                        "resource": t.resource,
                        "provider": t.provider,
                        "status": t.status.value,
                    }
                    for t in all_tasks
                ],
            },
        )

        return all_tasks

    async def _run_task(self, task: Task, used_providers: set[str]) -> None:
        await event_bus.emit("task.started", {"resource": task.resource, "provider": task.provider})

        if task.provider not in registry.names():
            logger.warning(
                "Provider '{}' not registered, skipping resource '{}'",
                task.provider,
                task.resource,
            )
            task.status = TaskStatus.SKIPPED
            await self._emit_task_completed(task)
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
                await self._emit_task_completed(task)
                return
            used_providers.add(task.provider)
            timeout_config = TimeoutConfig(timeout_seconds=task.timeout_seconds)
            await execute_with_timeout(
                provider.execute(task), timeout_config, task.id, task.resource
            )
            task.status = TaskStatus.SUCCESS
        except TaskTimeoutError as exc:
            logger.warning(
                "Task '{}' timed out after {}s, marking as failed",
                task.resource,
                exc.timeout,
            )
            task.status = TaskStatus.FAILED
        except Exception:
            logger.exception("Failed to execute task for resource '{}'", task.resource)
            task.status = TaskStatus.FAILED
        await self._emit_task_completed(task)

    async def _skip_dependency_failed(self, task: Task, blocking: list[str]) -> None:
        await event_bus.emit("task.started", {"resource": task.resource, "provider": task.provider})
        logger.warning(
            "Dependency of resource '{}' did not succeed ({}), skipping",
            task.resource,
            ", ".join(blocking),
        )
        task.status = TaskStatus.SKIPPED_DEPENDENCY_FAILED
        await self._emit_task_completed(task)

    async def _emit_task_completed(self, task: Task) -> None:
        await event_bus.emit(
            "task.completed",
            {
                "resource": task.resource,
                "provider": task.provider,
                "status": task.status.value,
            },
        )
