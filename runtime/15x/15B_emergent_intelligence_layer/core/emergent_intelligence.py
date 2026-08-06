"""15B — Emergent Intelligence Layer: Emergence Detector & Pattern Crystallizer"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import math
import time


@dataclass
class Signal:
    source: str
    value: float
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EmergentPattern:
    pattern_id: str
    description: str
    supporting_signals: list[str]
    confidence: float
    first_seen: float = field(default_factory=time.time)
    frequency: int = 1


@dataclass
class Attractor:
    name: str
    basin: dict[str, float]  # dimension -> value at attractor
    stability: float = 0.5


class EmergenceDetector:
    """Detects emergent patterns from streams of agent signals."""

    def __init__(self, window_size: int = 100, threshold: float = 0.75) -> None:
        self._window: list[Signal] = []
        self._window_size = window_size
        self._threshold = threshold
        self._patterns: dict[str, EmergentPattern] = {}
        self._attractors: list[Attractor] = []

    def ingest(self, signal: Signal) -> None:
        self._window.append(signal)
        if len(self._window) > self._window_size:
            self._window = self._window[-self._window_size:]

    def detect(self) -> list[EmergentPattern]:
        if len(self._window) < 5:
            return []
        new_patterns: list[EmergentPattern] = []
        sources = list({s.source for s in self._window})
        for i in range(len(sources)):
            for j in range(i + 1, len(sources)):
                correlation = self._correlate(sources[i], sources[j])
                if correlation >= self._threshold:
                    pid = f"{sources[i]}×{sources[j]}"
                    if pid in self._patterns:
                        self._patterns[pid].frequency += 1
                        self._patterns[pid].confidence = min(0.99, correlation)
                    else:
                        pat = EmergentPattern(
                            pattern_id=pid,
                            description=f"Correlated emergence between {sources[i]} and {sources[j]}",
                            supporting_signals=[sources[i], sources[j]],
                            confidence=correlation,
                        )
                        self._patterns[pid] = pat
                        new_patterns.append(pat)
        return new_patterns

    def _correlate(self, src_a: str, src_b: str) -> float:
        vals_a = [s.value for s in self._window if s.source == src_a]
        vals_b = [s.value for s in self._window if s.source == src_b]
        if not vals_a or not vals_b:
            return 0.0
        min_len = min(len(vals_a), len(vals_b))
        vals_a, vals_b = vals_a[-min_len:], vals_b[-min_len:]
        mean_a = sum(vals_a) / len(vals_a)
        mean_b = sum(vals_b) / len(vals_b)
        cov = sum((a - mean_a) * (b - mean_b) for a, b in zip(vals_a, vals_b))
        std_a = math.sqrt(sum((v - mean_a) ** 2 for v in vals_a) + 1e-9)
        std_b = math.sqrt(sum((v - mean_b) ** 2 for v in vals_b) + 1e-9)
        return abs(cov / (std_a * std_b))

    def register_attractor(self, attractor: Attractor) -> None:
        self._attractors.append(attractor)

    def complexity_score(self) -> float:
        if not self._window:
            return 0.0
        sources = {s.source for s in self._window}
        unique_values = len({round(s.value, 1) for s in self._window})
        return math.log1p(len(sources)) * math.log1p(unique_values)

    def top_patterns(self, n: int = 5) -> list[EmergentPattern]:
        return sorted(self._patterns.values(), key=lambda p: p.confidence, reverse=True)[:n]
