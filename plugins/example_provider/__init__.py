"""
Example STARCORE plugin.

Registers a no-op provider to validate the plugin loading mechanism.
Use this as a template for real plugins: implement BaseProvider and
expose a register(registry) function.
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


def register(registry) -> None:
    if "noop" not in registry.names():
        registry.register(NoopProvider())
