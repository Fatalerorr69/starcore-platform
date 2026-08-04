"""
Blueprint Executor

`depends_on` is a success gate, not just an ordering constraint (ADR-010):
a step only reaches provider.execute() once every resource it depends on
has reached TaskStatus.SUCCESS. See Scheduler for the identical contract on
the concurrent path.
"""

from __future__ import annotations

import uuid

from core.events import event_bus
from core.tracing import get_tracer
from loguru import logger
from orchestrator.task import Task, TaskStatus
from orchestrator.timeout import (
    TaskTimeoutError,
    TimeoutConfig,
    TimeoutStrategy,
    execute_with_timeout,
)
from provider_sdk.registry import register_default_providers, registry

from .models import Blueprint
from .planner import ExecutionPlanner


class BlueprintExecutor:
    async def execute(self, blueprint: Blueprint) -> list[Task]:
        register_default_providers()
        plan = ExecutionPlanner().create_plan(blueprint)

        tasks: list[Task] = []
        used_providers: set[str] = set()
        status_by_resource: dict[str, TaskStatus] = {}

        with get_tracer().start_as_current_span("blueprint.execute") as span:
            span.set_attribute("blueprint.name", blueprint.name)
            span.set_attribute("blueprint.version", blueprint.version)
            for step in plan:
                task = self._build_task(step)
                tasks.append(task)
                await event_bus.emit(
                    "task.started", {"resource": task.resource, "provider": task.provider}
                )
                await self._dispatch_task(task, step, used_providers, status_by_resource)

        await self._finalize_run(tasks, used_providers, blueprint)
        return tasks

    def _build_task(self, step: dict) -> Task:
        return Task(
            id=str(uuid.uuid4()),
            provider=step["provider"],
            action="create",
            resource=step["resource"],
            payload=step["config"],
            kind=step["kind"],
            depends_on=list(step.get("depends_on", [])),
            timeout_seconds=step.get("timeout_seconds"),
            timeout_strategy=step.get("timeout_strategy"),
        )

    async def _dispatch_task(
        self,
        task: Task,
        step: dict,
        used_providers: set[str],
        status_by_resource: dict[str, TaskStatus],
    ) -> None:
        blocking = [
            dep for dep in task.depends_on if status_by_resource.get(dep) != TaskStatus.SUCCESS
        ]
        if blocking:
            logger.warning(
                "Dependency of resource '{}' did not succeed ({}), skipping",
                task.resource,
                ", ".join(blocking),
            )
            task.status = TaskStatus.SKIPPED_DEPENDENCY_FAILED
            status_by_resource[task.resource] = task.status
            await self._emit_task_completed(task)
            return

        if step["provider"] not in registry.names():
            logger.warning(
                "Provider '{}' not registered, skipping resource '{}'",
                step["provider"],
                step["resource"],
            )
            task.status = TaskStatus.SKIPPED
            status_by_resource[task.resource] = task.status
            await self._emit_task_completed(task)
            return

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
                status_by_resource[task.resource] = task.status
                await self._emit_task_completed(task)
                return

            used_providers.add(step["provider"])
            timeout_config = TimeoutConfig(
                timeout_seconds=task.timeout_seconds,
                strategy=task.timeout_strategy or TimeoutStrategy.CANCEL,
            )
            with get_tracer().start_as_current_span("task.dispatch") as tspan:
                tspan.set_attribute("task.resource", task.resource)
                tspan.set_attribute("task.provider", task.provider)
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
            logger.exception("Failed to execute task for resource '{}'", step["resource"])
            task.status = TaskStatus.FAILED

        status_by_resource[task.resource] = task.status
        await self._emit_task_completed(task)

    async def _finalize_run(
        self,
        tasks: list[Task],
        used_providers: set[str],
        blueprint: Blueprint,
    ) -> None:
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

    async def _emit_task_completed(self, task: Task) -> None:
        await event_bus.emit(
            "task.completed",
            {
                "resource": task.resource,
                "provider": task.provider,
                "status": task.status.value,
            },
        )
