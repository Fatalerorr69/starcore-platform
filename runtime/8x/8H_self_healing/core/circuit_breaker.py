"""8H — Self-Healing Fabric: Circuit Breaker"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failures: int = field(default=0, init=False)
    _last_failure: float = field(default=0.0, init=False)

    def call(self, fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
            else:
                raise RuntimeError(f"Circuit {self.name} is OPEN")
        try:
            result = fn(*args, **kwargs)
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
                self._failures = 0
            return result
        except Exception as exc:
            self._failures += 1
            self._last_failure = time.time()
            if self._failures >= self.failure_threshold:
                self._state = CircuitState.OPEN
            raise exc

    @property
    def state(self) -> CircuitState:
        return self._state
