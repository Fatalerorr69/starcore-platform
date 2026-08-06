"""17I — Universal Ethics Framework: multi-principle ethical assessment."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time


class EthicalFramework(str, Enum):
    UTILITARIAN = "utilitarian"
    DEONTOLOGICAL = "deontological"
    VIRTUE_ETHICS = "virtue_ethics"
    CARE_ETHICS = "care_ethics"
    CONTRACTARIAN = "contractarian"


@dataclass
class EthicalDimension:
    framework: EthicalFramework
    score: float
    reasoning: str
    weight: float = 1.0


@dataclass
class EthicalAction:
    action_id: str
    description: str
    stakeholders: list[str] = field(default_factory=list)
    impacts: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EthicalAssessment:
    action_id: str
    dimensions: list[EthicalDimension]
    overall_score: float
    recommendation: str
    timestamp: float = field(default_factory=time.time)

    @property
    def is_ethical(self) -> bool:
        return self.overall_score >= 0.5


class UniversalEthicsFramework:
    def __init__(self) -> None:
        self._weights: dict[EthicalFramework, float] = {
            EthicalFramework.UTILITARIAN: 0.30,
            EthicalFramework.DEONTOLOGICAL: 0.25,
            EthicalFramework.VIRTUE_ETHICS: 0.20,
            EthicalFramework.CARE_ETHICS: 0.15,
            EthicalFramework.CONTRACTARIAN: 0.10,
        }
        self._assessments: list[EthicalAssessment] = []

    def _utilitarian(self, action: EthicalAction) -> float:
        if not action.impacts:
            return 0.5
        return (sum(action.impacts.values()) / len(action.impacts) + 1.0) / 2.0

    def _deontological(self, action: EthicalAction) -> float:
        if any(v < -0.5 for v in action.impacts.values()):
            return 0.1
        return 0.8

    def _virtue(self, action: EthicalAction) -> float:
        if not action.impacts:
            return 0.5
        vals = list(action.impacts.values())
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / len(vals)
        return max(0.0, 1.0 - var)

    def _care(self, action: EthicalAction) -> float:
        if not action.impacts:
            return 0.5
        return sum(1 for v in action.impacts.values() if v > 0) / len(action.impacts)

    def _contractarian(self, action: EthicalAction) -> float:
        if not action.impacts:
            return 0.5
        return 0.9 if all(v >= 0 for v in action.impacts.values()) else 0.2

    def assess(self, action: EthicalAction) -> EthicalAssessment:
        scorers = {
            EthicalFramework.UTILITARIAN: self._utilitarian,
            EthicalFramework.DEONTOLOGICAL: self._deontological,
            EthicalFramework.VIRTUE_ETHICS: self._virtue,
            EthicalFramework.CARE_ETHICS: self._care,
            EthicalFramework.CONTRACTARIAN: self._contractarian,
        }
        dimensions = [
            EthicalDimension(fw, round(scorer(action), 4),
                             f"{fw.value} evaluation", self._weights[fw])
            for fw, scorer in scorers.items()
        ]
        total_w = sum(d.weight for d in dimensions)
        overall = sum(d.score * d.weight for d in dimensions) / total_w
        assessment = EthicalAssessment(
            action_id=action.action_id,
            dimensions=dimensions,
            overall_score=round(overall, 4),
            recommendation="APPROVE" if overall >= 0.5 else "REJECT",
        )
        self._assessments.append(assessment)
        return assessment

    def framework_stats(self) -> dict[str, Any]:
        return {
            "assessments": len(self._assessments),
            "approved": sum(1 for a in self._assessments if a.recommendation == "APPROVE"),
        }
