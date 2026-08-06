"""8D — Marketplace Fabric: Plugin Registry"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Plugin:
    name: str
    version: str
    author: str
    capabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        key = f"{plugin.name}:{plugin.version}"
        self._plugins[key] = plugin

    def resolve(self, name: str) -> Plugin | None:
        matches = [p for k, p in self._plugins.items() if k.startswith(f"{name}:") and p.enabled]
        if not matches:
            return None
        return sorted(matches, key=lambda p: p.version, reverse=True)[0]

    def list_enabled(self) -> list[Plugin]:
        return [p for p in self._plugins.values() if p.enabled]
