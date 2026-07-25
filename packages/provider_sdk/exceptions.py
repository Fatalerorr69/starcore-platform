"""
Provider Exceptions
"""


class ProviderError(Exception):
    """Base exception for all provider-related errors."""


class ProviderConnectionError(ProviderError):
    """Raised when a provider fails to connect."""


class ResourceNotFoundError(ProviderError):
    """Raised when a requested resource does not exist."""
