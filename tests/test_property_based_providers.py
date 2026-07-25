"""
Property-Based Tests — Providers

Verifies structural invariants for ProviderRegistry, BaseProvider,
DockerProvider, and ProxmoxProvider that must hold for all valid inputs.
"""

from __future__ import annotations

import asyncio

import pytest
from hypothesis import given
from hypothesis import strategies as st
from provider_sdk.base import BaseProvider
from provider_sdk.registry import ProviderRegistry

# ── Strategies ─────────────────────────────────────────────────────────────────

_PROVIDER_NAME = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz-",
    min_size=1,
    max_size=16,
)


def _make_provider(name: str) -> BaseProvider:
    """Return a minimal concrete BaseProvider with the given name."""

    class _P(BaseProvider):
        async def connect(self) -> bool:
            return True

        async def disconnect(self) -> None:
            return None

        async def health(self) -> dict:
            return {"status": "ok", "provider": self.name}

        async def list_resources(self) -> list[dict]:
            return []

        async def execute(self, task) -> None:
            return None

    p = _P()
    p.name = name
    return p


# ── ProviderRegistry properties ────────────────────────────────────────────────


@given(names=st.lists(_PROVIDER_NAME, min_size=1, max_size=10, unique=True))
def test_registry_names_is_always_sorted(names: list[str]) -> None:
    """ProviderRegistry.names() returns a sorted list for any set of registrations."""
    reg = ProviderRegistry()
    for name in names:
        reg.register(_make_provider(name))

    result = reg.names()
    assert result == sorted(result)


@given(names=st.lists(_PROVIDER_NAME, min_size=1, max_size=10, unique=True))
def test_registry_get_returns_same_instance(names: list[str]) -> None:
    """get(name) returns the exact provider object that was registered."""
    reg = ProviderRegistry()
    providers = {name: _make_provider(name) for name in names}
    for p in providers.values():
        reg.register(p)

    for name, original in providers.items():
        assert reg.get(name) is original


@given(names=st.lists(_PROVIDER_NAME, min_size=1, max_size=10, unique=True))
def test_registry_all_count_matches_unique_names(names: list[str]) -> None:
    """len(list(all())) always equals len(names()) after registering unique providers."""
    reg = ProviderRegistry()
    for name in names:
        reg.register(_make_provider(name))

    assert len(list(reg.all())) == len(reg.names())


@given(
    name=_PROVIDER_NAME,
    n=st.integers(min_value=2, max_value=5),
)
def test_registry_duplicate_register_last_write_wins(name: str, n: int) -> None:
    """Registering the same name N times keeps only the last-registered instance."""
    reg = ProviderRegistry()
    last: BaseProvider | None = None
    for _ in range(n):
        p = _make_provider(name)
        reg.register(p)
        last = p

    assert reg.get(name) is last
    assert reg.names() == [name]
    assert len(list(reg.all())) == 1


@given(names=st.lists(_PROVIDER_NAME, min_size=1, max_size=10, unique=True))
def test_registry_names_consistent_with_all(names: list[str]) -> None:
    """The set returned by names() matches the names of every provider in all()."""
    reg = ProviderRegistry()
    for name in names:
        reg.register(_make_provider(name))

    assert set(reg.names()) == {p.name for p in reg.all()}


# ── BaseProvider._connect_lock properties ─────────────────────────────────────


@given(n=st.integers(min_value=1, max_value=8))
def test_connect_lock_is_asyncio_lock(n: int) -> None:
    """_connect_lock is an asyncio.Lock on every concrete provider instance."""
    import asyncio

    for _ in range(n):
        p = _make_provider("test")
        assert isinstance(p._connect_lock, asyncio.Lock)


@given(n=st.integers(min_value=2, max_value=8))
def test_connect_lock_same_object_on_repeated_access(n: int) -> None:
    """_connect_lock returns the identical Lock object on every access for a given instance."""
    p = _make_provider("test")
    first = p._connect_lock
    for _ in range(n - 1):
        assert p._connect_lock is first


@given(n=st.integers(min_value=2, max_value=8))
def test_connect_lock_unique_per_provider_instance(n: int) -> None:
    """Two distinct provider instances never share the same lock object."""
    providers = [_make_provider(f"p{i}") for i in range(n)]
    locks = [p._connect_lock for p in providers]
    assert len(set(id(lock) for lock in locks)) == n


# ── DockerProvider pure-logic properties ──────────────────────────────────────

_DOCKER_VALID_ACTIONS = {"create", "start", "stop", "remove"}
_DOCKER_INVALID_ACTION = st.text(min_size=1).filter(lambda a: a not in _DOCKER_VALID_ACTIONS)


@given(n=st.integers(min_value=1, max_value=4))
def test_docker_health_returns_disconnected_when_client_none(n: int) -> None:
    """DockerProvider.health() always reports disconnected when _client is None."""
    from providers.docker.provider import DockerProvider

    for _ in range(n):
        provider = DockerProvider()
        assert provider._client is None
        result = asyncio.run(provider.health())
        assert result["status"] == "disconnected"
        assert result["provider"] == "docker"


@given(n=st.integers(min_value=1, max_value=4))
def test_docker_list_resources_returns_empty_when_client_none(n: int) -> None:
    """DockerProvider.list_resources() returns [] when _client is None."""
    from providers.docker.provider import DockerProvider

    for _ in range(n):
        provider = DockerProvider()
        assert asyncio.run(provider.list_resources()) == []


@given(action=_DOCKER_INVALID_ACTION)
def test_docker_execute_raises_value_error_for_unsupported_action(action: str) -> None:
    """DockerProvider.execute() raises ValueError for any action not in the supported set."""
    from orchestrator.task import Task
    from providers.docker.provider import DockerProvider

    provider = DockerProvider()
    provider._client = object()  # type: ignore[assignment]  # non-None sentinel

    task = Task(id="t", provider="docker", action=action, resource="r")
    with pytest.raises(ValueError, match="Unsupported Docker action"):
        asyncio.run(provider.execute(task))


# ── ProxmoxProvider pure-logic properties ─────────────────────────────────────

_PROXMOX_VALID_ACTIONS = {
    "create",
    "destroy",
    "start",
    "stop",
    "shutdown",
    "snapshot-create",
    "snapshot-list",
    "snapshot-delete",
    "snapshot-rollback",
}
_PROXMOX_INVALID_ACTION = st.text(min_size=1).filter(lambda a: a not in _PROXMOX_VALID_ACTIONS)


@given(n=st.integers(min_value=1, max_value=4))
def test_proxmox_health_returns_disconnected_when_client_none(n: int) -> None:
    """ProxmoxProvider.health() always reports disconnected when _client is None."""
    from providers.proxmox.provider import ProxmoxProvider

    for _ in range(n):
        provider = ProxmoxProvider()
        assert provider._client is None
        result = asyncio.run(provider.health())
        assert result["status"] == "disconnected"
        assert result["provider"] == "proxmox"


@given(n=st.integers(min_value=1, max_value=4))
def test_proxmox_list_resources_returns_empty_when_client_none(n: int) -> None:
    """ProxmoxProvider.list_resources() returns [] when _client is None."""
    from providers.proxmox.provider import ProxmoxProvider

    for _ in range(n):
        provider = ProxmoxProvider()
        assert asyncio.run(provider.list_resources()) == []


@given(action=_PROXMOX_INVALID_ACTION)
def test_proxmox_execute_raises_value_error_for_unsupported_action(action: str) -> None:
    """ProxmoxProvider.execute() raises ValueError for any action not in the supported set."""
    from orchestrator.task import Task
    from providers.proxmox.provider import ProxmoxProvider

    provider = ProxmoxProvider()
    provider._client = object()  # type: ignore[assignment]  # non-None sentinel

    task = Task(id="t", provider="proxmox", action=action, resource="r")
    with pytest.raises(ValueError, match="Unsupported Proxmox action"):
        asyncio.run(provider.execute(task))
