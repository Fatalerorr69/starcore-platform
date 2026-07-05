"""
Provider Exceptions
"""


class ProviderError(Exception):
    pass


class ConnectionError(ProviderError):
    pass


class AuthenticationError(ProviderError):
    pass


class ResourceNotFound(ProviderError):
    pass
