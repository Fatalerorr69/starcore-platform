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


async def test_unsubscribe_stops_future_calls():
    bus = EventBus()
    received = []
    bus.subscribe("e", received.append)
    await bus.emit("e", 1)
    bus.unsubscribe("e", received.append)
    await bus.emit("e", 2)
    assert received == [1]


async def test_unsubscribe_nonexistent_callback_is_safe():
    bus = EventBus()
    bus.unsubscribe("e", lambda x: x)  # must not raise


async def test_unsubscribe_does_not_affect_other_subscribers():
    bus = EventBus()
    a_calls: list[int] = []
    b_calls: list[int] = []
    bus.subscribe("e", a_calls.append)
    bus.subscribe("e", b_calls.append)
    bus.unsubscribe("e", a_calls.append)
    await bus.emit("e", 99)
    assert a_calls == []
    assert b_calls == [99]
