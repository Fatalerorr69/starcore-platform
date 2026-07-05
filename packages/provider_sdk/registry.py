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
