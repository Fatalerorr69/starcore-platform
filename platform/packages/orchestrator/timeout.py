"""
Task Timeout Support for STARCORE Orchestrator

Provides configurable timeout behavior for task execution with:
- Per-task timeout configuration
- Graceful timeout handling
- Task status tracking
- Comprehensive logging
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import StrEnum

from loguru import logger


class TaskTimeoutError(Exception):
    """Raised when a task execution exceeds configured timeout."""

    def __init__(self, task_id: str, resource: str, timeout: float) -> None:
        self.task_id = task_id
        self.resource = resource
        self.timeout = timeout
        super().__init__(f"Task {task_id} (resource='{resource}') exceeded timeout of {timeout}s")


class TimeoutStrategy(StrEnum):
    """Strategy for handling timeout.

    Attributes:
        CANCEL: Immediately cancel the task (default).
        WAIT_AND_MARK: Wait for task to complete, then mark as timed out.
        IGNORE: Continue waiting, just log warning.
    """

    CANCEL = "cancel"
    WAIT_AND_MARK = "wait_and_mark"
    IGNORE = "ignore"


@dataclass
class TimeoutConfig:
    """Configuration for task timeout behavior.

    Attributes:
        timeout_seconds: Timeout in seconds (None = no timeout).
        strategy: How to handle timeout (default: CANCEL).
    """

    timeout_seconds: float | None = None
    strategy: TimeoutStrategy = TimeoutStrategy.CANCEL

    def is_enabled(self) -> bool:
        """Check if timeout is enabled."""
        return self.timeout_seconds is not None and self.timeout_seconds > 0


async def execute_with_timeout(
    coro,
    config: TimeoutConfig,
    task_id: str,
    resource: str,
):
    """Execute a coroutine with timeout.

    Args:
        coro: Coroutine to execute.
        config: Timeout configuration.
        task_id: Task ID for logging.
        resource: Resource name for logging.

    Returns:
        Result of coro.

    Raises:
        TaskTimeoutError: If timeout is exceeded and strategy is CANCEL or
            WAIT_AND_MARK (when the grace period also expires).
    """
    if not config.is_enabled():
        return await coro

    assert config.timeout_seconds is not None  # is_enabled() checked above guarantees this
    timeout: float = config.timeout_seconds

    logger.debug(f"Executing task {task_id} (resource='{resource}') with timeout {timeout}s")

    if config.strategy in (TimeoutStrategy.WAIT_AND_MARK, TimeoutStrategy.IGNORE):
        # Wrap in a Task so asyncio.shield() protects the underlying work from
        # being cancelled when asyncio.wait_for fires on the shield wrapper.
        # asyncio.wait_for cancels its *argument* on timeout; shield absorbs that
        # cancellation so the inner Task keeps running after the first deadline.
        inner: asyncio.Task = asyncio.create_task(coro)
        try:
            return await asyncio.wait_for(asyncio.shield(inner), timeout=timeout)
        except TimeoutError:
            logger.warning(
                f"Task {task_id} (resource='{resource}') exceeded timeout of "
                f"{timeout}s (strategy={config.strategy.value})"
            )
            if config.strategy == TimeoutStrategy.IGNORE:
                logger.warning(
                    f"Ignoring timeout for task {task_id} (strategy=IGNORE), continuing..."
                )
                return await inner
            # WAIT_AND_MARK: inner Task is still running; give it a grace period.
            logger.warning(f"Waiting for task {task_id} to complete (may exceed timeout)")
            try:
                return await asyncio.wait_for(asyncio.shield(inner), timeout=timeout * 0.5)
            except TimeoutError:
                inner.cancel()
                raise TaskTimeoutError(task_id, resource, timeout) from None

    # CANCEL strategy (default) and unknown strategies — no shield needed.
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except TimeoutError:
        logger.warning(
            f"Task {task_id} (resource='{resource}') exceeded timeout of "
            f"{timeout}s (strategy={config.strategy.value})"
        )
        if config.strategy == TimeoutStrategy.CANCEL:
            logger.error(f"Cancelling task {task_id} due to timeout")
            raise TaskTimeoutError(task_id, resource, timeout) from None
        raise ValueError(f"Unknown timeout strategy: {config.strategy}") from None
