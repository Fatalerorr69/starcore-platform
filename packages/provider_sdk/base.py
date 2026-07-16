"""
Provider SDK
Base Provider Interface
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """Abstract infrastructure provider.

    A concrete provider (e.g.
    :class:`~providers.docker.provider.DockerProvider`,
    :class:`~providers.proxmox.provider.ProxmoxProvider`) is registered once
    per process as a long-lived singleton in the global
    :class:`~provider_sdk.registry.ProviderRegistry`. Because the same
    instance is shared, :meth:`connect` may be invoked concurrently by
    multiple in-flight orchestration tasks that target resources on this
    provider within the same execution wave -- see
    :meth:`~orchestrator.scheduler.Scheduler.execute`, which dispatches every
    dependency-satisfied task of a wave concurrently via ``asyncio.gather``.

    Subclasses are responsible for making their own :meth:`connect` (and,
    where relevant, :meth:`disconnect`) implementation safe under this
    concurrent-call pattern. The protected :attr:`_connect_lock` property is
    provided for exactly this purpose: a subclass's :meth:`connect` should
    acquire it before inspecting or mutating its connection state, so that
    only the first concurrent caller performs the actual connection work and
    every other concurrent caller observes the already-established
    connection instead of racing to replace it.

    Adding :attr:`_connect_lock` does not change the abstract contract of
    this class: all five abstract methods below are unchanged, and existing
    subclasses that do not use :attr:`_connect_lock` continue to work
    exactly as before.
    """

    name: str = "provider"
    version: str = "1.0.0"

    @property
    def _connect_lock(self) -> asyncio.Lock:
        """A lock private to this provider instance, guarding connection setup.

        The lock is created lazily on first access rather than in
        ``__init__``, so that subclasses are not required to call
        ``super().__init__()`` in order to benefit from it. Exactly one
        :class:`asyncio.Lock` is created per provider instance and reused
        for that instance's lifetime; two different provider instances never
        share a lock.
        """
        lock: asyncio.Lock | None = getattr(self, "_connect_lock_impl", None)
        if lock is None:
            lock = asyncio.Lock()
            self._connect_lock_impl: asyncio.Lock = lock
        return lock

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to provider."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from provider."""

    @abstractmethod
    async def health(self) -> dict[str, Any]:
        """Return provider health."""

    @abstractmethod
    async def list_resources(self) -> list[dict]:
        """List managed resources."""

    @abstractmethod
    async def execute(self, task) -> None:
        """Execute orchestration task."""
