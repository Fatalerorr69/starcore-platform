"""
Provider SDK - Retry Logic with Exponential Backoff

Provides configurable retry behavior for provider operations with:
- Exponential backoff
- Jitter to prevent thundering herd
- Selective exception retrying
- Comprehensive logging
"""

from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from loguru import logger


@dataclass
class RetryConfig:
    """Configuration for retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts (default: 3).
        base_delay: Initial delay in seconds (default: 1.0).
        max_delay: Maximum delay between retries (default: 30.0).
        exponential_base: Base for exponential backoff (default: 2.0).
        jitter: Whether to add random jitter to delay (default: True).
        retryable_exceptions: Tuple of exception types to retry on.
    """

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple[type[Exception], ...] = (
        ConnectionError,
        TimeoutError,
        OSError,
    )

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt number.

        Args:
            attempt: Zero-indexed attempt number.

        Returns:
            Delay in seconds, capped at max_delay.
        """
        delay = self.base_delay * (self.exponential_base**attempt)
        delay = min(delay, self.max_delay)
        if self.jitter:
            delay = random.uniform(0, delay)
        return delay


class RetryableError(Exception):
    """Raised when all retry attempts are exhausted."""

    def __init__(self, message: str, last_exception: Exception) -> None:
        self.message = message
        self.last_exception = last_exception
        super().__init__(f"{message}: {last_exception}")


async def attempt_with_retry[T](
    operation: Callable[..., Awaitable[T]],
    config: RetryConfig | None = None,
    operation_name: str = "operation",
    **operation_kwargs,
) -> T:
    """Attempt an async operation with exponential backoff retry.

    Args:
        operation: Async callable to retry.
        config: Retry configuration (uses defaults if None).
        operation_name: Human-readable name for logging.
        **operation_kwargs: Keyword arguments to pass to operation.

    Returns:
        Result of operation.

    Raises:
        RetryableError: If all retries are exhausted.
        Exception: If exception is not retryable (raised immediately).
    """
    if config is None:
        config = RetryConfig()

    for attempt in range(config.max_retries + 1):
        try:
            logger.debug(
                f"Attempting {operation_name} (attempt {attempt + 1}/{config.max_retries + 1})"
            )
            result = await operation(**operation_kwargs)
            if attempt > 0:
                logger.info(f"{operation_name} succeeded after {attempt} retry(ies)")
            return result
        except Exception as exc:
            is_retryable = any(
                isinstance(exc, exc_type) for exc_type in config.retryable_exceptions
            )

            if not is_retryable:
                logger.debug(f"{operation_name} failed with non-retryable error: {exc}")
                raise

            if attempt >= config.max_retries:
                logger.error(
                    f"{operation_name} failed after {config.max_retries} retries: {exc}"
                )
                raise RetryableError(
                    f"{operation_name} failed after {config.max_retries} retries",
                    exc,
                ) from exc

            delay = config.calculate_delay(attempt)
            logger.warning(
                f"{operation_name} failed: {exc}. Retrying in {delay:.1f}s "
                f"(attempt {attempt + 1}/{config.max_retries})..."
            )
            await asyncio.sleep(delay)

    raise RuntimeError("Retry logic reached unreachable state")  # pragma: no cover
