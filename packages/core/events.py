"""
Simple Event Bus
"""

from __future__ import annotations

import inspect
from collections import defaultdict
from collections.abc import Callable
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, callback: Callable) -> None:
        self._subscribers[event].append(callback)

    async def emit(self, event: str, payload: Any = None) -> None:
        for callback in list(self._subscribers[event]):
            result = callback(payload)
            if inspect.isawaitable(result):
                await result


event_bus = EventBus()
