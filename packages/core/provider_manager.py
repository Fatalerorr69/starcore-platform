"""
Infrastructure Providers
"""


class ProviderManager:
    def __init__(self):
        self.providers = {}

    def register(self, provider):
        self.providers[provider.name] = provider

    def get(self, name):
        return self.providers.get(name)

    def available(self):
        return list(self.providers.keys())
