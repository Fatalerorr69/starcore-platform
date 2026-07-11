"""
Simple Event Bus
"""

from collections import defaultdict
from collections.abc import Callable


class EventBus:

    def __init__(self):
        self._events = defaultdict(list)

    def subscribe(self, event: str, callback: Callable):
        self._events[event].append(callback)

    def emit(self, event: str, payload=None):

        for callback in self._events[event]:
            callback(payload)


event_bus = EventBus()
