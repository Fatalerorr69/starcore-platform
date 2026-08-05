"""
Tests for provider_sdk exception hierarchy.
"""

import pytest
from provider_sdk.exceptions import ProviderConnectionError, ProviderError, ResourceNotFoundError


def test_provider_error_is_an_exception():
    with pytest.raises(ProviderError):
        raise ProviderError("base error")


def test_provider_connection_error_is_provider_error():
    with pytest.raises(ProviderError):
        raise ProviderConnectionError("could not connect")


def test_resource_not_found_is_provider_error():
    with pytest.raises(ProviderError):
        raise ResourceNotFoundError("vm-101 not found")


def test_exception_messages_are_preserved():
    exc = ProviderConnectionError("timeout after 30s")
    assert "timeout" in str(exc)

    exc2 = ResourceNotFoundError("no such container")
    assert "no such container" in str(exc2)
