"""
Property-Based Tests — orchestrator.timeout

Verifies structural invariants for TimeoutConfig, TaskTimeoutError, and
execute_with_timeout that must hold for all valid inputs.
"""

from __future__ import annotations

import asyncio

from hypothesis import given, settings
from hypothesis import strategies as st
from orchestrator.timeout import TaskTimeoutError, TimeoutConfig, TimeoutStrategy

# ── Strategies ─────────────────────────────────────────────────────────────────

_POSITIVE_FLOAT = st.floats(
    min_value=0.001, max_value=1000.0, allow_nan=False, allow_infinity=False
)
_NON_POSITIVE_FLOAT = st.floats(
    max_value=0.0, allow_nan=False, allow_infinity=False
)
_TASK_ID = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-_", min_size=1, max_size=40)
_RESOURCE = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-_", min_size=1, max_size=40)


# ── TimeoutConfig.is_enabled invariants ───────────────────────────────────────


@given(timeout=_POSITIVE_FLOAT)
def test_timeout_config_is_enabled_for_any_positive_value(timeout: float) -> None:
    """TimeoutConfig.is_enabled() is True for any timeout_seconds > 0."""
    assert TimeoutConfig(timeout_seconds=timeout).is_enabled()


@given(timeout=_NON_POSITIVE_FLOAT)
def test_timeout_config_is_disabled_for_non_positive(timeout: float) -> None:
    """TimeoutConfig.is_enabled() is False for any timeout_seconds <= 0."""
    assert not TimeoutConfig(timeout_seconds=timeout).is_enabled()


def test_timeout_config_is_disabled_when_none() -> None:
    """TimeoutConfig.is_enabled() is False when timeout_seconds is None."""
    assert not TimeoutConfig(timeout_seconds=None).is_enabled()


@given(timeout=_POSITIVE_FLOAT, strategy=st.sampled_from(list(TimeoutStrategy)))
def test_timeout_config_never_raises_for_valid_inputs(
    timeout: float, strategy: TimeoutStrategy
) -> None:
    """TimeoutConfig construction never raises for any valid timeout and strategy."""
    config = TimeoutConfig(timeout_seconds=timeout, strategy=strategy)
    assert config.timeout_seconds == timeout
    assert config.strategy == strategy


# ── TaskTimeoutError invariants ────────────────────────────────────────────────


@given(task_id=_TASK_ID, resource=_RESOURCE, timeout=_POSITIVE_FLOAT)
def test_task_timeout_error_attributes_always_match_constructor(
    task_id: str, resource: str, timeout: float
) -> None:
    """TaskTimeoutError always stores the exact task_id, resource, and timeout passed in."""
    err = TaskTimeoutError(task_id, resource, timeout)
    assert err.task_id == task_id
    assert err.resource == resource
    assert err.timeout == timeout


@given(task_id=_TASK_ID, resource=_RESOURCE, timeout=_POSITIVE_FLOAT)
def test_task_timeout_error_str_contains_all_fields(
    task_id: str, resource: str, timeout: float
) -> None:
    """str(TaskTimeoutError) always contains task_id and resource."""
    err = TaskTimeoutError(task_id, resource, timeout)
    msg = str(err)
    assert task_id in msg
    assert resource in msg


@given(task_id=_TASK_ID, resource=_RESOURCE, timeout=_POSITIVE_FLOAT)
def test_task_timeout_error_is_exception(
    task_id: str, resource: str, timeout: float
) -> None:
    """TaskTimeoutError is always an Exception subclass and can be raised/caught."""
    err = TaskTimeoutError(task_id, resource, timeout)
    assert isinstance(err, Exception)

    try:
        raise err
    except TaskTimeoutError as caught:
        assert caught is err


# ── execute_with_timeout disabled-path invariant ───────────────────────────────


@given(
    timeout=st.one_of(st.none(), st.just(0.0), _NON_POSITIVE_FLOAT),
    value=st.integers(min_value=-1000, max_value=1000),
)
@settings(max_examples=40)
def test_execute_with_timeout_disabled_always_passes_through(
    timeout: float | None, value: int
) -> None:
    """When timeout is disabled (None or <= 0), execute_with_timeout always returns the coro result.
    """
    from orchestrator.timeout import execute_with_timeout

    async def constant() -> int:
        return value

    config = TimeoutConfig(timeout_seconds=timeout)
    result = asyncio.run(execute_with_timeout(constant(), config, "t", "r"))
    assert result == value
