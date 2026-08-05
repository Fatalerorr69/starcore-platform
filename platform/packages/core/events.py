"""
Simple Event Bus
"""

from __future__ import annotations

import contextvars
import inspect
from collections import defaultdict
from collections.abc import Callable
from typing import Any

# Per-streaming-session correlation token. Set by SSE/WS generators before
# creating their exec_task so the task inherits the value via context copy.
# emit() injects it as "_stream_id" into every dict payload while it is set,
# allowing each streaming handler to filter out events from other concurrent
# runs without touching the executor or scheduler.
_STREAM_CTX: contextvars.ContextVar[str] = contextvars.ContextVar("_stream_id", default="")


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, callback: Callable) -> None:
        self._subscribers[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        try:
            self._subscribers[event].remove(callback)
        except ValueError:
            pass

    async def emit(self, event: str, payload: Any = None) -> None:
        if isinstance(payload, dict):
            stream_id = _STREAM_CTX.get()
            if stream_id:
                payload = {**payload, "_stream_id": stream_id}
        for callback in list(self._subscribers[event]):
            result = callback(payload)
            if inspect.isawaitable(result):
                await result


event_bus = EventBus()
