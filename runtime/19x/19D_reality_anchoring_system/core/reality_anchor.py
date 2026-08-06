"""19D — Reality Anchoring System: ground-truth validation and drift detection."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AnchorPoint:
    anchor_id: str
    name: str
    value: float
    tolerance: float = 0.1

    def is_valid(self, observed: float) -> bool:
        return abs(observed - self.value) <= self.tolerance


@dataclass
class RealityDrift:
    anchor_id: str
    expected: float
    observed: float

    @property
    def magnitude(self) -> float:
        return abs(self.observed - self.expected)

    @property
    def is_critical(self) -> bool:
        ref = abs(self.expected)
        if ref < 1e-9:
            return self.magnitude > 1.0
        return self.magnitude > ref * 0.5


class RealityAnchoringSystem:
    def __init__(self) -> None:
        self._anchors: dict[str, AnchorPoint] = {}
        self._drifts: list[RealityDrift] = []
        self._checks: int = 0

    def register_anchor(self, anchor: AnchorPoint) -> None:
        self._anchors[anchor.anchor_id] = anchor

    def check(self, observations: dict[str, float]) -> list[RealityDrift]:
        drifts: list[RealityDrift] = []
        for aid, value in observations.items():
            if aid in self._anchors:
                anchor = self._anchors[aid]
                if not anchor.is_valid(value):
                    drift = RealityDrift(anchor_id=aid,
                                        expected=anchor.value, observed=value)
                    drifts.append(drift)
                    self._drifts.append(drift)
        self._checks += 1
        return drifts

    def stability_score(self) -> float:
        if not self._anchors:
            return 1.0
        recent = self._drifts[-len(self._anchors):]
        return max(0.0, 1.0 - len(recent) / max(1, len(self._anchors)))

    def system_stats(self) -> dict[str, Any]:
        return {
            "anchors": len(self._anchors),
            "total_drifts": len(self._drifts),
            "checks": self._checks,
            "stability": round(self.stability_score(), 4),
        }
