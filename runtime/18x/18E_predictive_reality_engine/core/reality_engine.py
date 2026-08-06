"""18E — Predictive Reality Engine: linear extrapolation timeline forecasting."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RealityState:
    timestamp: float
    variables: dict[str, float] = field(default_factory=dict)

    def delta(self, other: "RealityState") -> dict[str, float]:
        keys = set(self.variables) | set(other.variables)
        return {k: other.variables.get(k, 0.0) - self.variables.get(k, 0.0)
                for k in keys}


@dataclass
class TimelineEvent:
    event_id: str
    timestamp: float
    state: RealityState
    probability: float = 1.0


class PredictiveRealityEngine:
    def __init__(self, horizon: int = 10) -> None:
        self._horizon = horizon
        self._history: list[RealityState] = []
        self._predictions: list[TimelineEvent] = []
        self._tick: float = 0.0

    def observe(self, state: RealityState) -> None:
        self._history.append(state)
        self._tick = state.timestamp

    def predict(self, steps: int = 1) -> list[TimelineEvent]:
        if len(self._history) < 2:
            return []
        s1, s2 = self._history[-2], self._history[-1]
        delta = s1.delta(s2)
        events: list[TimelineEvent] = []
        for i in range(1, steps + 1):
            future = {k: s2.variables.get(k, 0.0) + delta.get(k, 0.0) * i
                      for k in set(s2.variables) | set(delta)}
            prob = max(0.0, 1.0 - i * 0.1)
            events.append(TimelineEvent(
                event_id=f"pred_{int(self._tick)}_{i}",
                timestamp=self._tick + i,
                state=RealityState(timestamp=self._tick + i, variables=future),
                probability=prob,
            ))
        self._predictions = events
        return events

    def divergence(self, actual: RealityState) -> float:
        if not self._predictions:
            return 0.0
        pred = min(self._predictions, key=lambda e: abs(e.timestamp - actual.timestamp))
        diffs = [abs(actual.variables.get(k, 0.0) - pred.state.variables.get(k, 0.0))
                 for k in actual.variables]
        return sum(diffs) / max(1, len(diffs))

    def engine_stats(self) -> dict[str, Any]:
        return {
            "history_length": len(self._history),
            "predictions": len(self._predictions),
            "current_tick": self._tick,
        }
