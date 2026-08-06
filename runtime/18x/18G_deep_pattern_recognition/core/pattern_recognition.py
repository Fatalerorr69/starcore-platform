"""18G — Deep Pattern Recognition: sliding-window fingerprint pattern mining."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import hashlib


@dataclass
class PatternSignature:
    pattern_id: str
    fingerprint: str
    frequency: int = 1
    confidence: float = 1.0

    def reinforce(self) -> None:
        self.frequency += 1
        self.confidence = min(1.0, self.confidence + 0.05)


class DeepPatternEngine:
    def __init__(self, window_size: int = 5) -> None:
        self._window = window_size
        self._patterns: dict[str, PatternSignature] = {}
        self._buffer: list[Any] = []
        self._observations: int = 0

    def _fingerprint(self, sequence: list[Any]) -> str:
        data = str(sequence).encode()
        return hashlib.md5(data).hexdigest()[:8]

    def observe(self, value: Any) -> list[PatternSignature]:
        self._buffer.append(value)
        self._observations += 1
        detected: list[PatternSignature] = []
        for size in range(2, min(self._window, len(self._buffer)) + 1):
            window = self._buffer[-size:]
            fp = self._fingerprint(window)
            if fp in self._patterns:
                self._patterns[fp].reinforce()
                detected.append(self._patterns[fp])
            else:
                sig = PatternSignature(
                    pattern_id=f"pat_{len(self._patterns)}",
                    fingerprint=fp,
                )
                self._patterns[fp] = sig
        return detected

    def top_patterns(self, n: int = 5) -> list[PatternSignature]:
        return sorted(self._patterns.values(),
                      key=lambda p: p.frequency, reverse=True)[:n]

    def engine_stats(self) -> dict[str, Any]:
        return {
            "patterns": len(self._patterns),
            "observations": self._observations,
            "top_frequency": max((p.frequency for p in self._patterns.values()), default=0),
        }
