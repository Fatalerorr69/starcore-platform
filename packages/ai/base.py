"""
AI Provider — abstract base class and shared utilities.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

_FENCE_RE = re.compile(r"^```(?:yaml|yml)?\s*|\s*```$", re.MULTILINE)


class BlueprintGenerationError(Exception):
    """Raised when a blueprint cannot be generated."""


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences that models sometimes emit despite instructions."""
    return _FENCE_RE.sub("", text).strip()


class AIProvider(ABC):
    """Abstract base for AI-backed blueprint generators."""

    @abstractmethod
    async def generate_blueprint_yaml(self, description: str) -> str: ...

    # Convenience alias so providers can call self._strip_fences(text).
    _strip_fences = staticmethod(_strip_code_fences)
