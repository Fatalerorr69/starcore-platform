"""
Provider SDK
Base Provider Interface
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """
    Abstract infrastructure provider.
    """

    name: str = "provider"
    version: str = "1.0.0"

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
