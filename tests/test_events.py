"""
Event Bus Tests
"""

from __future__ import annotations

from core.events import EventBus


async def test_emit_calls_sync_subscriber():
    bus = EventBus()
    received = []
    bus.subscribe("thing.happened", received.append)

    await bus.emit("thing.happened", {"value": 42})

    assert received == [{"value": 42}]


async def test_emit_calls_async_subscriber():
    bus = EventBus()
    received = []

    async def handler(payload):
        received.append(payload)

    bus.subscribe("thing.happened", handler)

    await bus.emit("thing.happened", {"value": 1})

    assert received == [{"value": 1}]


async def test_emit_with_no_subscribers_does_not_raise():
    bus = EventBus()
    await bus.emit("nothing.subscribed", {"value": 1})


async def test_subscribers_only_called_for_matching_event():
    bus = EventBus()
    a_calls = []
    b_calls = []
    bus.subscribe("a", a_calls.append)
    bus.subscribe("b", b_calls.append)

    await bus.emit("a", "payload")

    assert a_calls == ["payload"]
    assert b_calls == []
