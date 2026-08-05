"""Tests for orchestrator.timeout — TimeoutConfig, TaskTimeoutError, execute_with_timeout."""

from __future__ import annotations

import asyncio

import pytest
from orchestrator.timeout import (
    TaskTimeoutError,
    TimeoutConfig,
    TimeoutStrategy,
    execute_with_timeout,
)

# ── TimeoutConfig ─────────────────────────────────────────────────────────────


def test_timeout_config_disabled_when_none():
    assert not TimeoutConfig(timeout_seconds=None).is_enabled()


def test_timeout_config_disabled_when_zero():
    assert not TimeoutConfig(timeout_seconds=0).is_enabled()


def test_timeout_config_enabled_with_positive():
    assert TimeoutConfig(timeout_seconds=5.0).is_enabled()


# ── TaskTimeoutError ──────────────────────────────────────────────────────────


def test_task_timeout_error_attributes():
    err = TaskTimeoutError("task-1", "my-resource", 30.0)
    assert err.task_id == "task-1"
    assert err.resource == "my-resource"
    assert err.timeout == 30.0
    assert "task-1" in str(err)
    assert "my-resource" in str(err)
    assert "30.0" in str(err)


# ── execute_with_timeout ──────────────────────────────────────────────────────


def test_execute_with_timeout_no_timeout_passes_through():
    async def fast():
        return "result"

    config = TimeoutConfig(timeout_seconds=None)
    result = asyncio.run(execute_with_timeout(fast(), config, "t1", "r1"))
    assert result == "result"


def test_execute_with_timeout_zero_disabled_passes_through():
    async def fast():
        return 42

    config = TimeoutConfig(timeout_seconds=0)
    result = asyncio.run(execute_with_timeout(fast(), config, "t1", "r1"))
    assert result == 42


def test_execute_with_timeout_task_completes_before_timeout():
    async def fast():
        return "fast"

    config = TimeoutConfig(timeout_seconds=10.0, strategy=TimeoutStrategy.CANCEL)
    result = asyncio.run(execute_with_timeout(fast(), config, "t1", "r1"))
    assert result == "fast"


def test_execute_with_timeout_wait_and_mark_completes_before_timeout():
    async def fast():
        return "fast"

    config = TimeoutConfig(timeout_seconds=10.0, strategy=TimeoutStrategy.WAIT_AND_MARK)
    result = asyncio.run(execute_with_timeout(fast(), config, "t1", "r1"))
    assert result == "fast"


def test_execute_with_timeout_ignore_completes_before_timeout():
    async def fast():
        return "fast"

    config = TimeoutConfig(timeout_seconds=10.0, strategy=TimeoutStrategy.IGNORE)
    result = asyncio.run(execute_with_timeout(fast(), config, "t1", "r1"))
    assert result == "fast"


def test_execute_with_timeout_cancel_strategy_raises():
    async def slow():
        await asyncio.sleep(10)

    config = TimeoutConfig(timeout_seconds=0.01, strategy=TimeoutStrategy.CANCEL)
    with pytest.raises(TaskTimeoutError) as exc_info:
        asyncio.run(execute_with_timeout(slow(), config, "task-x", "res-x"))
    assert exc_info.value.task_id == "task-x"
    assert exc_info.value.resource == "res-x"
    assert exc_info.value.timeout == 0.01


def test_execute_with_timeout_wait_and_mark_second_timeout_raises():
    async def slow():
        await asyncio.sleep(10)

    config = TimeoutConfig(timeout_seconds=0.01, strategy=TimeoutStrategy.WAIT_AND_MARK)
    with pytest.raises(TaskTimeoutError):
        asyncio.run(execute_with_timeout(slow(), config, "t1", "r1"))


def test_execute_with_timeout_wait_and_mark_succeeds_on_second_try():
    # Coroutine sleeps 0.12 s; first timeout fires at 0.1 s leaving 0.02 s
    # remaining.  Grace period is 0.1 * 0.5 = 0.05 s, so the task finishes
    # inside the grace window and the result is returned normally.
    async def slightly_slow():
        await asyncio.sleep(0.12)
        return "done"

    config = TimeoutConfig(timeout_seconds=0.1, strategy=TimeoutStrategy.WAIT_AND_MARK)
    result = asyncio.run(execute_with_timeout(slightly_slow(), config, "t1", "r1"))
    assert result == "done"


def test_execute_with_timeout_ignore_strategy_continues():
    async def eventual():
        await asyncio.sleep(0.05)
        return "eventual"

    config = TimeoutConfig(timeout_seconds=0.01, strategy=TimeoutStrategy.IGNORE)
    result = asyncio.run(execute_with_timeout(eventual(), config, "t1", "r1"))
    assert result == "eventual"


def test_execute_with_timeout_unknown_strategy_raises():
    class _FakeStrategy(str):
        value = "unknown_strategy"

    async def slow():
        await asyncio.sleep(10)

    config = TimeoutConfig(
        timeout_seconds=0.01,
        strategy=_FakeStrategy("unknown_strategy"),  # type: ignore[arg-type]
    )
    with pytest.raises(ValueError, match="Unknown timeout strategy"):
        asyncio.run(execute_with_timeout(slow(), config, "t1", "r1"))
