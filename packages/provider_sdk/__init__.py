"""Provider SDK for STARCORE Platform.

Public API:
- BaseProvider: Abstract base class for all providers
- ProviderRegistry: Global singleton registry
- ProviderException: Base exception for provider errors
- RetryConfig: Configuration for retry behavior
- attempt_with_retry(): Helper for retryable operations
"""

from .base import BaseProvider
from .exceptions import ProviderException
from .registry import ProviderRegistry, register_default_providers, registry
from .retry import RetryConfig, RetryableError, attempt_with_retry

__all__ = [
    "BaseProvider",
    "ProviderRegistry",
    "ProviderException",
    "RetryConfig",
    "RetryableError",
    "attempt_with_retry",
    "register_default_providers",
    "registry",
]
