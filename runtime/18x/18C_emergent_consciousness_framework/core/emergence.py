"""18C — Emergent Consciousness Framework: integration theory of consciousness."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConsciousnessLevel(str, Enum):
    DORMANT = "dormant"
    REACTIVE = "reactive"
    ADAPTIVE = "adaptive"
    AWARE = "aware"
    SELF_AWARE = "self_aware"


_THRESHOLDS: list[tuple[float, ConsciousnessLevel]] = [
    (0.8, ConsciousnessLevel.SELF_AWARE),
    (0.6, ConsciousnessLevel.AWARE),
    (0.4, ConsciousnessLevel.ADAPTIVE),
    (0.2, ConsciousnessLevel.REACTIVE),
    (0.0, ConsciousnessLevel.DORMANT),
]


@dataclass
class EmergentProperty:
    name: str
    strength: float = 0.0
    interactions: int = 0

    def emerge(self, stimulus: float) -> float:
        self.interactions += 1
        self.strength = min(1.0, self.strength + stimulus / (self.interactions + 1))
        return self.strength


class EmergenceEngine:
    def __init__(self) -> None:
        self._properties: dict[str, EmergentProperty] = {}
        self._integration: float = 0.0
        self._steps: int = 0

    def add_property(self, prop: EmergentProperty) -> None:
        self._properties[prop.name] = prop

    def stimulate(self, stimuli: dict[str, float]) -> dict[str, float]:
        results: dict[str, float] = {}
        for name, strength in stimuli.items():
            if name not in self._properties:
                self._properties[name] = EmergentProperty(name)
            results[name] = self._properties[name].emerge(strength)
        if self._properties:
            self._integration = (sum(p.strength for p in self._properties.values()) /
                                  len(self._properties))
        self._steps += 1
        return results

    @property
    def consciousness_level(self) -> ConsciousnessLevel:
        for threshold, level in _THRESHOLDS:
            if self._integration >= threshold:
                return level
        return ConsciousnessLevel.DORMANT

    def report(self) -> dict[str, Any]:
        return {
            "properties": len(self._properties),
            "integration": round(self._integration, 4),
            "level": self.consciousness_level.value,
            "steps": self._steps,
        }
