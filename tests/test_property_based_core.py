"""
Property-Based Tests — Core

Verifies structural invariants for EventBus, PluginManager, and the
run-history repository that must hold for all valid inputs.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

from core.events import EventBus
from core.main import _resolve_request_id
from core.plugin_manager import PluginManager
from core.repository import get_run, list_known_provider_vmids, list_runs, save_run
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from orchestrator.task import Task, TaskStatus

# ── Strategies ─────────────────────────────────────────────────────────────────

_NAME = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz-",
    min_size=1,
    max_size=20,
)
_SHORT_ID = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz",
    min_size=1,
    max_size=12,
)
_EVENT_NAME = st.sampled_from(
    ["task.started", "task.completed", "run.completed", "custom.event", "another.event"]
)


def _make_task(tid: str, provider: str = "fake", status: TaskStatus = TaskStatus.SUCCESS) -> Task:
    return Task(id=tid, provider=provider, action="create", resource=tid, status=status)


# ── EventBus properties ────────────────────────────────────────────────────────


@given(
    event=_EVENT_NAME,
    n=st.integers(min_value=1, max_value=8),
    payload=st.one_of(st.none(), st.integers(), st.text(max_size=20)),
)
def test_event_bus_emit_calls_all_registered_callbacks(event: str, n: int, payload: Any) -> None:
    """Every callback subscribed to an event is called exactly once on emit."""
    bus = EventBus()
    calls: list[Any] = []
    for _ in range(n):
        bus.subscribe(event, lambda p, _calls=calls: _calls.append(p))

    asyncio.run(bus.emit(event, payload))

    assert len(calls) == n


@given(
    event=_EVENT_NAME,
    payload=st.one_of(st.none(), st.integers(min_value=-100, max_value=100), st.text(max_size=20)),
)
def test_event_bus_emit_passes_payload_to_every_callback(event: str, payload: Any) -> None:
    """Each subscribed callback receives the exact payload passed to emit."""
    bus = EventBus()
    received: list[Any] = []
    for _ in range(3):
        bus.subscribe(event, lambda p, _recv=received: _recv.append(p))

    asyncio.run(bus.emit(event, payload))

    assert all(p == payload for p in received)


@given(
    subscribed_event=_EVENT_NAME,
    emitted_event=_EVENT_NAME,
    n=st.integers(min_value=1, max_value=5),
)
def test_event_bus_callbacks_not_called_for_other_events(
    subscribed_event: str, emitted_event: str, n: int
) -> None:
    """Callbacks subscribed to event A are never called when event B is emitted."""
    # Only meaningful when the two events differ
    if subscribed_event == emitted_event:
        return

    bus = EventBus()
    calls: list[Any] = []
    for _ in range(n):
        bus.subscribe(subscribed_event, lambda p, _calls=calls: _calls.append(p))

    asyncio.run(bus.emit(emitted_event, "payload"))

    assert calls == []


@given(
    event=_EVENT_NAME,
    payload=st.integers(),
)
def test_event_bus_emit_with_no_subscribers_is_a_noop(event: str, payload: int) -> None:
    """emit() on an event with zero subscribers completes without error."""
    bus = EventBus()
    asyncio.run(bus.emit(event, payload))  # must not raise


@given(
    event=_EVENT_NAME,
    n=st.integers(min_value=1, max_value=6),
)
def test_event_bus_callbacks_invoked_in_subscription_order(event: str, n: int) -> None:
    """Callbacks are invoked in the order they were subscribed (FIFO)."""
    bus = EventBus()
    order: list[int] = []
    for i in range(n):
        bus.subscribe(event, lambda p, _i=i, _order=order: _order.append(_i))

    asyncio.run(bus.emit(event))

    assert order == list(range(n))


@given(
    event=_EVENT_NAME,
    n_sync=st.integers(min_value=0, max_value=3),
    n_async=st.integers(min_value=0, max_value=3),
)
def test_event_bus_handles_mixed_sync_and_async_callbacks(
    event: str, n_sync: int, n_async: int
) -> None:
    """emit() correctly awaits async callbacks alongside sync ones."""
    if n_sync + n_async == 0:
        return

    bus = EventBus()
    calls: list[str] = []

    for i in range(n_sync):
        bus.subscribe(event, lambda p, _i=i, _c=calls: _c.append(f"sync-{_i}"))

    for i in range(n_async):

        async def _async_cb(p: Any, _i: int = i, _c: list = calls) -> None:
            _c.append(f"async-{_i}")

        bus.subscribe(event, _async_cb)

    asyncio.run(bus.emit(event))

    assert len(calls) == n_sync + n_async


# ── PluginManager properties ───────────────────────────────────────────────────


@given(names=st.lists(_SHORT_ID, min_size=1, max_size=10, unique=True))
def test_plugin_manager_names_is_always_sorted(names: list[str]) -> None:
    """PluginManager.names() returns a sorted list for any set of registrations."""
    pm = PluginManager()
    for name in names:
        pm.register(name, object())

    result = pm.names()
    assert result == sorted(result)


@given(names=st.lists(_SHORT_ID, min_size=1, max_size=10, unique=True))
def test_plugin_manager_get_returns_registered_instance(names: list[str]) -> None:
    """get(name) returns the exact object that was registered."""
    pm = PluginManager()
    plugins = {name: object() for name in names}
    for name, plugin in plugins.items():
        pm.register(name, plugin)

    for name, original in plugins.items():
        assert pm.get(name) is original


@given(
    name=_SHORT_ID,
    n=st.integers(min_value=2, max_value=5),
)
def test_plugin_manager_duplicate_register_last_write_wins(name: str, n: int) -> None:
    """Registering the same name N times keeps only the last-registered plugin."""
    pm = PluginManager()
    last: object | None = None
    for _ in range(n):
        plugin = object()
        pm.register(name, plugin)
        last = plugin

    assert pm.get(name) is last
    assert pm.names() == [name]
    assert len(pm.names()) == 1


@given(names=st.lists(_SHORT_ID, min_size=1, max_size=10, unique=True))
def test_plugin_manager_names_consistent_with_registered_plugins(
    names: list[str],
) -> None:
    """set(names()) equals the set of names passed to register()."""
    pm = PluginManager()
    for name in names:
        pm.register(name, object())

    assert set(pm.names()) == set(names)


@given(name=_SHORT_ID)
def test_plugin_manager_get_returns_none_for_unregistered_name(name: str) -> None:
    """get() returns None for a plugin that was never registered."""
    pm = PluginManager()
    assert pm.get(name) is None


# ── Repository properties ──────────────────────────────────────────────────────


@given(
    bp_name=_NAME,
    version=st.text(alphabet="0123456789.", min_size=1, max_size=10),
    parallel=st.booleans(),
    task_ids=st.lists(_SHORT_ID, min_size=0, max_size=5, unique=True),
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_repository_save_and_get_run_round_trips_blueprint_fields(
    bp_name: str, version: str, parallel: bool, task_ids: list[str]
) -> None:
    """get_run(id) returns a record whose blueprint_name, version, and parallel match save_run()."""
    from core.database import get_session

    tasks = [_make_task(tid) for tid in task_ids]
    session = get_session()
    try:
        run = save_run(session, bp_name, version, parallel, tasks)
        fetched = get_run(session, run.id)
        assert fetched is not None
        assert fetched.blueprint_name == bp_name
        assert fetched.version == version
        assert fetched.parallel == parallel
    finally:
        session.close()


@given(
    bp_name=_NAME,
    task_ids=st.lists(_SHORT_ID, min_size=1, max_size=4, unique=True),
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_repository_save_run_persists_all_task_records(bp_name: str, task_ids: list[str]) -> None:
    """The saved run contains exactly as many task records as tasks passed to save_run()."""
    from core.database import get_session

    tasks = [_make_task(tid) for tid in task_ids]
    session = get_session()
    try:
        run = save_run(session, bp_name, "1.0", False, tasks)
        fetched = get_run(session, run.id)
        assert fetched is not None
        assert len(fetched.tasks) == len(task_ids)
    finally:
        session.close()


@given(
    bp_name=_NAME,
    limit=st.integers(min_value=0, max_value=10),
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_repository_list_runs_limit_returns_at_most_k_records(bp_name: str, limit: int) -> None:
    """list_runs(limit=k) returns at most k records regardless of total DB state."""
    from core.database import get_session

    session = get_session()
    try:
        result = list_runs(session, limit=limit)
        assert len(result) <= limit
    finally:
        session.close()


@given(
    provider=st.sampled_from(["proxmox", "docker", "fake"]),
    vmids=st.lists(st.integers(min_value=100, max_value=9999), min_size=1, max_size=5, unique=True),
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_repository_list_known_provider_vmids_returns_saved_vmids(
    provider: str, vmids: list[int]
) -> None:
    """list_known_provider_vmids() returns vmids that were stored in task results."""
    from core.database import get_session

    tasks: list[Task] = []
    for vmid in vmids:
        t = _make_task(f"vmid-task-{provider}-{vmid}", provider=provider)
        t.result = {"vmid": vmid}
        tasks.append(t)

    session = get_session()
    try:
        save_run(session, "vmid-test", "1.0", False, tasks)
        found = list_known_provider_vmids(session, provider)
        for vmid in vmids:
            assert vmid in found
    finally:
        session.close()


# ── _resolve_request_id properties ──────────────────────────────────────────

_REQUEST_ID_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-"


def _is_valid_request_id_token(s: str) -> bool:
    return bool(s) and 1 <= len(s) <= 128 and all(c in _REQUEST_ID_ALPHABET for c in s)


@given(token=st.text(alphabet=_REQUEST_ID_ALPHABET, min_size=1, max_size=128))
def test_resolve_request_id_echoes_valid_token_unchanged(token: str) -> None:
    """A caller-supplied token matching the allowed pattern is returned unchanged."""
    assert _resolve_request_id(token) == token


@given(
    token=st.one_of(
        st.none(),
        st.text(max_size=30).filter(lambda s: not _is_valid_request_id_token(s)),
    )
)
def test_resolve_request_id_generates_valid_uuid4_for_invalid_input(token: str | None) -> None:
    """Any input not matching the allowed pattern (including None) falls back to a UUID4."""
    result = _resolve_request_id(token)
    parsed = uuid.UUID(result)
    assert str(parsed) == result
    assert parsed.version == 4


@given(token=st.text(alphabet=_REQUEST_ID_ALPHABET, min_size=129, max_size=200))
def test_resolve_request_id_rejects_tokens_over_128_chars(token: str) -> None:
    """A token longer than 128 characters is rejected even though every character is valid."""
    result = _resolve_request_id(token)
    assert result != token
    uuid.UUID(result)
