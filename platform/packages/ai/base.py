"""
AI Provider — abstract base class and shared utilities.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

_FENCE_RE = re.compile(r"^```(?:yaml|yml)?\s*|\s*```$", re.MULTILINE)


class BlueprintGenerationError(Exception):
    """Raised when a blueprint cannot be generated."""


class RetryableStatusError(Exception):
    """HTTP status code that should trigger a retry (e.g. 429, 503)."""

    def __init__(self, status_code: int, message: str = "") -> None:
        self.status_code = status_code
        super().__init__(message or f"HTTP {status_code}")


@dataclass
class TokenUsage:
    """Token counts from an AI generation call."""

    input_tokens: int | None = None
    output_tokens: int | None = None


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences that models sometimes emit despite instructions."""
    return _FENCE_RE.sub("", text).strip()


class AIProvider(ABC):
    """Abstract base for AI-backed blueprint generators."""

    _last_usage: TokenUsage | None = None

    @abstractmethod
    async def generate_blueprint_yaml(self, description: str) -> str: ...

    async def health_check(self) -> bool:
        """Quick connectivity check. Returns True if the provider is reachable."""
        return True

    # Convenience alias so providers can call self._strip_fences(text).
    _strip_fences = staticmethod(_strip_code_fences)
