"""Tests for provider_sdk.retry — RetryConfig, RetryableError, attempt_with_retry."""

from __future__ import annotations

import asyncio

import pytest
from provider_sdk.retry import RetryableError, RetryConfig, attempt_with_retry

# ── RetryConfig ───────────────────────────────────────────────────────────────


def test_retry_config_defaults():
    config = RetryConfig()
    assert config.max_retries == 3
    assert config.base_delay == 1.0
    assert config.max_delay == 30.0
    assert config.jitter is True


def test_retry_config_calculate_delay_no_jitter():
    config = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False, max_delay=30.0)
    assert config.calculate_delay(0) == 1.0
    assert config.calculate_delay(1) == 2.0
    assert config.calculate_delay(2) == 4.0


def test_retry_config_calculate_delay_caps_at_max():
    config = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False, max_delay=3.0)
    assert config.calculate_delay(5) == 3.0


def test_retry_config_calculate_delay_with_jitter():
    config = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=True, max_delay=30.0)
    for _ in range(20):
        delay = config.calculate_delay(1)
        assert 0 <= delay <= 2.0


# ── RetryableError ────────────────────────────────────────────────────────────


def test_retryable_error_stores_attributes():
    cause = ConnectionError("network down")
    err = RetryableError("op failed after 2 retries", cause)
    assert err.message == "op failed after 2 retries"
    assert err.last_exception is cause
    assert "op failed" in str(err)
    assert "network down" in str(err)


# ── attempt_with_retry ────────────────────────────────────────────────────────


def test_attempt_with_retry_success_on_first_try():
    async def op():
        return 42

    result = asyncio.run(attempt_with_retry(op, operation_name="test-op"))
    assert result == 42


def test_attempt_with_retry_uses_default_config_when_none():
    call_count = [0]

    async def op():
        call_count[0] += 1
        return "ok"

    result = asyncio.run(attempt_with_retry(op))
    assert result == "ok"
    assert call_count[0] == 1


def test_attempt_with_retry_non_retryable_raises_immediately():
    call_count = [0]

    async def op():
        call_count[0] += 1
        raise ValueError("not retryable")

    with pytest.raises(ValueError, match="not retryable"):
        asyncio.run(attempt_with_retry(op, operation_name="failing"))
    assert call_count[0] == 1


def test_attempt_with_retry_retries_on_retryable_and_succeeds():
    call_count = [0]

    async def op():
        call_count[0] += 1
        if call_count[0] < 3:
            raise ConnectionError("transient")
        return "ok"

    config = RetryConfig(max_retries=3, base_delay=0.0, jitter=False)
    result = asyncio.run(attempt_with_retry(op, config=config, operation_name="transient"))
    assert result == "ok"
    assert call_count[0] == 3


def test_attempt_with_retry_logs_success_after_retries():
    call_count = [0]

    async def op():
        call_count[0] += 1
        if call_count[0] == 1:
            raise ConnectionError("first attempt fails")
        return "recovered"

    config = RetryConfig(max_retries=2, base_delay=0.0, jitter=False)
    result = asyncio.run(attempt_with_retry(op, config=config, operation_name="recovering"))
    assert result == "recovered"


def test_attempt_with_retry_raises_retryable_error_when_exhausted():
    async def op():
        raise ConnectionError("always fails")

    config = RetryConfig(max_retries=2, base_delay=0.0, jitter=False)
    with pytest.raises(RetryableError) as exc_info:
        asyncio.run(attempt_with_retry(op, config=config, operation_name="failing"))
    assert isinstance(exc_info.value.last_exception, ConnectionError)
