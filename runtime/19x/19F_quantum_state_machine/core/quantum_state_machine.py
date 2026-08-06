"""19F — Quantum State Machine: probabilistic state superposition and transition."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class QState:
    state_id: str
    amplitude: complex = complex(1.0, 0.0)

    @property
    def probability(self) -> float:
        return abs(self.amplitude) ** 2


@dataclass
class QTransition:
    from_state: str
    to_state: str
    probability: float
    label: str = ""


class QuantumStateMachine:
    def __init__(self) -> None:
        self._states: dict[str, QState] = {}
        self._transitions: list[QTransition] = []
        self._current: dict[str, float] = {}
        self._steps: int = 0

    def add_state(self, state: QState) -> None:
        self._states[state.state_id] = state

    def add_transition(self, transition: QTransition) -> None:
        self._transitions.append(transition)

    def initialize(self, state_id: str) -> None:
        self._current = {state_id: 1.0}

    def step(self) -> dict[str, float]:
        """Propagate probability through transitions."""
        new_dist: dict[str, float] = {}
        for sid, prob in self._current.items():
            outgoing = [t for t in self._transitions if t.from_state == sid]
            if not outgoing:
                new_dist[sid] = new_dist.get(sid, 0.0) + prob
            else:
                for t in outgoing:
                    new_dist[t.to_state] = (new_dist.get(t.to_state, 0.0) +
                                             prob * t.probability)
        self._current = new_dist
        self._steps += 1
        return dict(self._current)

    def measure(self) -> str:
        """Collapse to most probable state."""
        if not self._current:
            return ""
        return max(self._current, key=lambda s: self._current[s])

    def machine_stats(self) -> dict[str, Any]:
        return {
            "states": len(self._states),
            "transitions": len(self._transitions),
            "steps": self._steps,
        }
