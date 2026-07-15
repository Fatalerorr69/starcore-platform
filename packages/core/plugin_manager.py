"""
Plugin Manager
"""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass
from pathlib import Path

from loguru import logger
from provider_sdk.registry import ProviderRegistry
from provider_sdk.registry import registry as provider_registry

from core.events import EventBus, event_bus


@dataclass
class PluginContext:
    registry: ProviderRegistry
    events: EventBus


class PluginManager:
    def __init__(self, plugins_dir: str = "plugins") -> None:
        self.plugins_dir = Path(plugins_dir)
        self.plugins: dict[str, object] = {}

    def discover(self) -> list[str]:
        if not self.plugins_dir.exists():
            return []

        discovered = []
        for plugin_path in sorted(self.plugins_dir.iterdir()):
            if plugin_path.is_dir() and (plugin_path / "__init__.py").exists():
                discovered.append(plugin_path.name)
        return discovered

    def load_all(self) -> list[str]:
        base_dir = str(self.plugins_dir.parent.resolve())
        if base_dir not in sys.path:
            sys.path.insert(0, base_dir)

        context = PluginContext(registry=provider_registry, events=event_bus)

        loaded: list[str] = []
        for name in self.discover():
            if name in self.plugins:
                loaded.append(name)
                continue

            module_name = f"{self.plugins_dir.name}.{name}"
            try:
                module = importlib.import_module(module_name)
            except ImportError as exc:
                logger.error("Failed to import plugin '{}': {}", name, exc)
                continue

            register_fn = getattr(module, "register", None)
            if register_fn is None:
                logger.warning("Plugin '{}' has no register() function, skipping", name)
                continue

            try:
                register_fn(context)
            except Exception:
                logger.exception("Plugin '{}' failed during register()", name)
                continue

            self.register(name, module)
            loaded.append(name)

        return loaded

    def register(self, name: str, plugin: object) -> None:
        self.plugins[name] = plugin

    def get(self, name: str) -> object | None:
        return self.plugins.get(name)

    def names(self) -> list[str]:
        return sorted(self.plugins.keys())


plugin_manager = PluginManager()
