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
from enum import Enum

from loguru import logger


class TaskTimeoutError(Exception):
    """Raised when a task execution exceeds configured timeout."""

    def __init__(self, task_id: str, resource: str, timeout: float) -> None:
        self.task_id = task_id
        self.resource = resource
        self.timeout = timeout
        super().__init__(
            f"Task {task_id} (resource='{resource}') exceeded timeout of {timeout}s"
        )


class TimeoutStrategy(str, Enum):
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
        TaskTimeoutError: If timeout is exceeded and strategy is CANCEL.
    """
    if not config.is_enabled():
        # No timeout configured
        return await coro

    try:
        logger.debug(
            f"Executing task {task_id} (resource='{resource}') with timeout {config.timeout_seconds}s"
        )
        result = await asyncio.wait_for(coro, timeout=config.timeout_seconds)
        return result
    except asyncio.TimeoutError:
        logger.warning(
            f"Task {task_id} (resource='{resource}') exceeded timeout of {config.timeout_seconds}s "
            f"(strategy={config.strategy.value})"
        )

        if config.strategy == TimeoutStrategy.CANCEL:
            logger.error(f"Cancelling task {task_id} due to timeout")
            raise TaskTimeoutError(task_id, resource, config.timeout_seconds) from None
        elif config.strategy == TimeoutStrategy.WAIT_AND_MARK:
            logger.warning(f"Waiting for task {task_id} to complete (may exceed timeout)")
            try:
                # Wait a bit longer for graceful completion
                result = await asyncio.wait_for(coro, timeout=config.timeout_seconds * 0.5)
                return result
            except asyncio.TimeoutError:
                raise TaskTimeoutError(task_id, resource, config.timeout_seconds) from None
        elif config.strategy == TimeoutStrategy.IGNORE:
            logger.warning(
                f"Ignoring timeout for task {task_id} (strategy=IGNORE), continuing..."
            )
            return await coro
        else:
            raise ValueError(f"Unknown timeout strategy: {config.strategy}")
