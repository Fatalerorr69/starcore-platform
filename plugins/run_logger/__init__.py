"""
Example STARCORE plugin that logs blueprint run completions.

Demonstrates subscribing to STARCORE's event bus via context.events.
Real plugins could use this pattern for webhooks, audit logs, alerts.

Duplicate-registration protection is handled by PluginManager itself
(it will not call register() twice for the same plugin on the same
manager instance), so this plugin does not need its own guard.
"""

from __future__ import annotations

from typing import Any

from loguru import logger

completed_runs: list[dict[str, Any]] = []


async def _on_run_completed(payload: dict[str, Any]) -> None:
    completed_runs.append(payload)
    logger.info(
        "[run_logger] Blueprint '{}' finished: {} task(s)",
        payload.get("blueprint_name", "<unknown>"),
        len(payload.get("tasks", [])),
    )


def register(context) -> None:
    context.events.subscribe("run.completed", _on_run_completed)
