"""
Resource Actions

Executes a single provider action against a specific resource, outside
of any blueprint. Useful for ad hoc lifecycle management, such as
tearing down a resource that a previous blueprint run created.
"""

from __future__ import annotations

import uuid
from typing import Any

from loguru import logger
from orchestrator.task import Task, TaskStatus
from provider_sdk.registry import register_default_providers, registry


async def execute_resource_action(
    provider_name: str,
    action: str,
    resource: str,
    kind: str = "",
    payload: dict[str, Any] | None = None,
) -> Task:
    register_default_providers()

    task = Task(
        id=str(uuid.uuid4()),
        provider=provider_name,
        action=action,
        resource=resource,
        kind=kind,
        payload=payload or {},
    )

    if provider_name not in registry.names():
        logger.warning("Provider '{}' is not registered", provider_name)
        task.status = TaskStatus.SKIPPED
        return task

    provider = registry.get(provider_name)
    connected = await provider.connect()
    if not connected:
        logger.warning("Provider '{}' failed to connect", provider_name)
        task.status = TaskStatus.FAILED
        return task

    task.status = TaskStatus.RUNNING
    try:
        await provider.execute(task)
        task.status = TaskStatus.SUCCESS
    except Exception as exc:
        logger.exception("Resource action '{}' failed for '{}'", action, resource)
        task.result["error"] = str(exc)
        task.status = TaskStatus.FAILED
    finally:
        await provider.disconnect()

    return task
