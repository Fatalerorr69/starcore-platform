"""18I — Unified Theory of Mind: weighted multi-layer cognitive integration."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MindLayer(str, Enum):
    SENSORY = "sensory"
    PERCEPTUAL = "perceptual"
    COGNITIVE = "cognitive"
    METACOGNITIVE = "metacognitive"
    TRANSCENDENT = "transcendent"


LAYER_WEIGHTS: dict[MindLayer, float] = {
    MindLayer.SENSORY: 0.10,
    MindLayer.PERCEPTUAL: 0.20,
    MindLayer.COGNITIVE: 0.30,
    MindLayer.METACOGNITIVE: 0.25,
    MindLayer.TRANSCENDENT: 0.15,
}


@dataclass
class MindState:
    layer: MindLayer
    activation: float = 0.0
    content: dict[str, Any] = field(default_factory=dict)


class UnifiedMind:
    def __init__(self) -> None:
        self._states: dict[MindLayer, MindState] = {
            layer: MindState(layer=layer) for layer in MindLayer
        }
        self._coherence: float = 0.0
        self._cycles: int = 0

    def activate_layer(self, layer: MindLayer, activation: float,
                       content: dict[str, Any] | None = None) -> None:
        state = self._states[layer]
        state.activation = max(0.0, min(1.0, activation))
        if content:
            state.content.update(content)

    def integrate(self) -> float:
        total = sum(LAYER_WEIGHTS[l] * s.activation for l, s in self._states.items())
        self._coherence = total
        self._cycles += 1
        return self._coherence

    def introspect(self) -> dict[str, Any]:
        return {
            "coherence": round(self._coherence, 4),
            "cycles": self._cycles,
            "layers": {
                l.value: {"activation": s.activation, "weight": LAYER_WEIGHTS[l]}
                for l, s in self._states.items()
            },
        }

    @property
    def dominant_layer(self) -> MindLayer:
        return max(self._states.items(), key=lambda kv: kv[1].activation)[0]
