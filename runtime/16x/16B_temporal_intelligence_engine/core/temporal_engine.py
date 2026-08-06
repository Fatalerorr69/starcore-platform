"""16B — Temporal Intelligence Engine: Periodic pattern detection."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import math
import time


@dataclass
class TemporalEvent:
    event_id: str
    timestamp: float
    payload: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass
class TemporalPattern:
    pattern_id: str
    description: str
    period_seconds: float
    confidence: float
    occurrences: int = 0
    last_seen: float = field(default_factory=time.time)


class TemporalIntelligence:
    def __init__(self, window_size: int = 1000) -> None:
        self._events: list[TemporalEvent] = []
        self._patterns: dict[str, TemporalPattern] = {}
        self._window_size = window_size

    def record_event(self, event: TemporalEvent) -> None:
        self._events.append(event)
        if len(self._events) > self._window_size:
            self._events = self._events[-self._window_size:]

    def detect_periodicity(self, tag: str, min_occurrences: int = 3) -> TemporalPattern | None:
        tagged = [e for e in self._events if tag in e.tags]
        if len(tagged) < min_occurrences:
            return None
        intervals = [tagged[i + 1].timestamp - tagged[i].timestamp
                     for i in range(len(tagged) - 1)]
        if not intervals:
            return None
        mean_interval = sum(intervals) / len(intervals)
        variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)
        std = math.sqrt(variance)
        confidence = max(0.0, 1.0 - (std / (mean_interval + 1e-9)))
        pattern = TemporalPattern(
            pattern_id=f"period_{tag}",
            description=f"Periodic pattern for tag '{tag}'",
            period_seconds=mean_interval,
            confidence=confidence,
            occurrences=len(tagged),
            last_seen=tagged[-1].timestamp,
        )
        self._patterns[pattern.pattern_id] = pattern
        return pattern

    def next_expected(self, pattern_id: str) -> float | None:
        p = self._patterns.get(pattern_id)
        return (p.last_seen + p.period_seconds) if p else None

    def event_count(self) -> int:
        return len(self._events)

    def pattern_summary(self) -> list[dict[str, Any]]:
        return [{"id": p.pattern_id, "period": p.period_seconds,
                 "confidence": p.confidence, "occurrences": p.occurrences}
                for p in self._patterns.values()]
