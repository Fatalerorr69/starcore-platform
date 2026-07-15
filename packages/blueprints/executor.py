"""
Blueprint Executor
"""

from __future__ import annotations

import uuid

from core.events import event_bus
from loguru import logger
from orchestrator.task import Task, TaskStatus
from provider_sdk.registry import register_default_providers, registry

from .models import Blueprint
from .planner import ExecutionPlanner


class BlueprintExecutor:
    async def execute(self, blueprint: Blueprint) -> list[Task]:
        register_default_providers()

        planner = ExecutionPlanner()
        plan = planner.create_plan(blueprint)

        tasks: list[Task] = []
        used_providers: set[str] = set()

        for step in plan:
            task = Task(
                id=str(uuid.uuid4()),
                provider=step["provider"],
                action="create",
                resource=step["resource"],
                payload=step["config"],
                kind=step["kind"],
            )
            tasks.append(task)

            await event_bus.emit(
                "task.started", {"resource": task.resource, "provider": task.provider}
            )

            if step["provider"] not in registry.names():
                logger.warning(
                    "Provider '{}' not registered, skipping resource '{}'",
                    step["provider"],
                    step["resource"],
                )
                task.status = TaskStatus.SKIPPED
                await self._emit_task_completed(task)
                continue

            task.status = TaskStatus.RUNNING
            try:
                provider = registry.get(step["provider"])
                connected = await provider.connect()
                if not connected:
                    logger.warning(
                        "Provider '{}' failed to connect, marking resource '{}' as failed",
                        step["provider"],
                        step["resource"],
                    )
                    task.status = TaskStatus.FAILED
                    await self._emit_task_completed(task)
                    continue

                used_providers.add(step["provider"])
                await provider.execute(task)
                task.status = TaskStatus.SUCCESS
            except Exception:
                logger.exception("Failed to execute task for resource '{}'", step["resource"])
                task.status = TaskStatus.FAILED

            await self._emit_task_completed(task)

        for name in used_providers:
            await registry.get(name).disconnect()

        await event_bus.emit(
            "run.completed",
            {
                "blueprint_name": blueprint.name,
                "version": blueprint.version,
                "tasks": [
                    {
                        "resource": t.resource,
                        "provider": t.provider,
                        "status": t.status.value,
                    }
                    for t in tasks
                ],
            },
        )

        return tasks

    async def _emit_task_completed(self, task: Task) -> None:
        await event_bus.emit(
            "task.completed",
            {
                "resource": task.resource,
                "provider": task.provider,
                "status": task.status.value,
            },
        )
