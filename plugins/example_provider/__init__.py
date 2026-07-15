"""
Example STARCORE plugin.

Registers a no-op provider to validate the plugin loading mechanism.
Use this as a template: register(context) receives context.registry
(to add custom providers) and context.events (to subscribe to
blueprint execution events - see plugins/run_logger for an example).
"""

from __future__ import annotations

from typing import Any

from provider_sdk.base import BaseProvider


class NoopProvider(BaseProvider):
    name = "noop"

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> None:
        return None

    async def health(self) -> dict[str, Any]:
        return {"status": "ok", "provider": self.name}

    async def list_resources(self) -> list[dict]:
        return []

    async def execute(self, task) -> None:
        return None


def register(context) -> None:
    if "noop" not in context.registry.names():
        context.registry.register(NoopProvider())
