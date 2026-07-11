"""
Provider Registry
"""

from provider_sdk.base import BaseProvider


class ProviderRegistry:
    def __init__(self):
        self._providers: dict[str, BaseProvider] = {}

    def register(self, provider: BaseProvider):
        self._providers[provider.name] = provider

    def get(self, name: str):
        return self._providers[name]

    def all(self):
        return self._providers.values()

    def names(self):
        return sorted(self._providers.keys())


registry = ProviderRegistry()


def register_default_providers() -> None:
    """Register all built-in providers into the global registry."""
    from providers.docker.provider import DockerProvider
    from providers.proxmox.provider import ProxmoxProvider

    for provider_cls in (DockerProvider, ProxmoxProvider):
        instance = provider_cls()
        if instance.name not in registry.names():
            registry.register(instance)
