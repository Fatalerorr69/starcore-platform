"""
Property-Based Tests — provider_sdk.retry

Verifies structural invariants for RetryConfig, RetryableError, and
attempt_with_retry that must hold for all valid inputs.
"""

from __future__ import annotations

import asyncio

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from provider_sdk.retry import RetryableError, RetryConfig, attempt_with_retry

# ── Strategies ─────────────────────────────────────────────────────────────────

_POSITIVE_FLOAT = st.floats(min_value=0.01, max_value=100.0, allow_nan=False, allow_infinity=False)
_NON_NEGATIVE_FLOAT = st.floats(
    min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False
)
_ATTEMPT = st.integers(min_value=0, max_value=10)
_MAX_RETRIES = st.integers(min_value=0, max_value=5)
_OP_NAME = st.text(alphabet="abcdefghijklmnopqrstuvwxyz_-", min_size=1, max_size=20)


# ── RetryConfig.calculate_delay invariants ─────────────────────────────────────


@given(
    base_delay=_POSITIVE_FLOAT,
    max_delay=_POSITIVE_FLOAT,
    exp_base=st.floats(min_value=1.1, max_value=4.0, allow_nan=False, allow_infinity=False),
    attempt=_ATTEMPT,
)
def test_calculate_delay_always_within_bounds(
    base_delay: float, max_delay: float, exp_base: float, attempt: int
) -> None:
    """calculate_delay() always returns a value in [0, max_delay]."""
    config = RetryConfig(
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exp_base,
        jitter=True,
    )
    delay = config.calculate_delay(attempt)
    assert 0 <= delay <= max_delay


@given(
    base_delay=_POSITIVE_FLOAT,
    max_delay=_POSITIVE_FLOAT,
    exp_base=st.floats(min_value=1.1, max_value=4.0, allow_nan=False, allow_infinity=False),
    attempt=_ATTEMPT,
)
def test_calculate_delay_no_jitter_is_deterministic(
    base_delay: float, max_delay: float, exp_base: float, attempt: int
) -> None:
    """With jitter=False, calculate_delay() returns the same value every call."""
    config = RetryConfig(
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exp_base,
        jitter=False,
    )
    assert config.calculate_delay(attempt) == config.calculate_delay(attempt)


@given(
    base_delay=_POSITIVE_FLOAT,
    max_delay=_POSITIVE_FLOAT,
    exp_base=st.floats(min_value=1.1, max_value=4.0, allow_nan=False, allow_infinity=False),
    attempt=_ATTEMPT,
)
def test_calculate_delay_no_jitter_never_exceeds_max(
    base_delay: float, max_delay: float, exp_base: float, attempt: int
) -> None:
    """With jitter=False, calculate_delay() is exactly min(base * exp^attempt, max_delay)."""
    config = RetryConfig(
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exp_base,
        jitter=False,
    )
    expected = min(base_delay * (exp_base**attempt), max_delay)
    assert abs(config.calculate_delay(attempt) - expected) < 1e-9


@given(
    base_delay=_POSITIVE_FLOAT,
    max_delay=_POSITIVE_FLOAT,
    exp_base=st.floats(min_value=1.1, max_value=4.0, allow_nan=False, allow_infinity=False),
    attempt_a=_ATTEMPT,
    attempt_b=_ATTEMPT,
)
def test_calculate_delay_no_jitter_monotone_with_attempt(
    base_delay: float, max_delay: float, exp_base: float, attempt_a: int, attempt_b: int
) -> None:
    """With jitter=False, a higher attempt number produces a delay >= a lower one (up to max_delay).
    """
    assume(attempt_a <= attempt_b)
    config = RetryConfig(
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exp_base,
        jitter=False,
    )
    assert config.calculate_delay(attempt_a) <= config.calculate_delay(attempt_b)


# ── RetryableError invariants ──────────────────────────────────────────────────


@given(
    message=st.text(min_size=1, max_size=100),
)
def test_retryable_error_message_attribute_matches(message: str) -> None:
    """RetryableError.message always equals the message argument."""
    cause = ValueError("underlying cause")
    err = RetryableError(message, cause)
    assert err.message == message


@given(
    message=st.text(min_size=1, max_size=100),
)
def test_retryable_error_last_exception_is_preserved(message: str) -> None:
    """RetryableError.last_exception is always the exact exception object passed in."""
    cause = ConnectionError("network gone")
    err = RetryableError(message, cause)
    assert err.last_exception is cause


@given(
    message=st.text(min_size=1, max_size=80),
)
def test_retryable_error_str_contains_message_and_cause(message: str) -> None:
    """str(RetryableError) always includes the message and the cause's text."""
    cause_text = "root cause detail"
    cause = OSError(cause_text)
    err = RetryableError(message, cause)
    assert message in str(err)
    assert cause_text in str(err)


# ── attempt_with_retry invariants ──────────────────────────────────────────────


@given(
    max_retries=_MAX_RETRIES,
    op_name=_OP_NAME,
)
@settings(max_examples=30)
def test_attempt_with_retry_zero_retries_calls_operation_once(
    max_retries: int, op_name: str
) -> None:
    """With max_retries=0, attempt_with_retry makes exactly 1 call and returns its result."""
    call_count = [0]

    async def op() -> str:
        call_count[0] += 1
        return "ok"

    config = RetryConfig(max_retries=0, base_delay=0.0, jitter=False)
    result = asyncio.run(attempt_with_retry(op, config=config, operation_name=op_name))
    assert result == "ok"
    assert call_count[0] == 1


@given(
    max_retries=st.integers(min_value=1, max_value=4),
    op_name=_OP_NAME,
)
@settings(max_examples=30)
def test_attempt_with_retry_non_retryable_always_propagates_immediately(
    max_retries: int, op_name: str
) -> None:
    """Non-retryable exceptions are always raised immediately, regardless of max_retries."""
    call_count = [0]

    async def op() -> None:
        call_count[0] += 1
        raise TypeError("not retryable")

    config = RetryConfig(max_retries=max_retries, base_delay=0.0, jitter=False)
    with pytest.raises(TypeError, match="not retryable"):
        asyncio.run(attempt_with_retry(op, config=config, operation_name=op_name))
    assert call_count[0] == 1
