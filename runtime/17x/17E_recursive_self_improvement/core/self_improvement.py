"""17E — Recursive Self-Improvement: agent that evaluates and improves itself."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time


class ImprovementType(str, Enum):
    PARAMETER_TUNING = "parameter_tuning"
    STRATEGY_SWITCH = "strategy_switch"
    ARCHITECTURE_CHANGE = "architecture_change"
    KNOWLEDGE_EXPANSION = "knowledge_expansion"


@dataclass
class ImprovementAction:
    action_id: str
    improvement_type: ImprovementType
    description: str
    expected_gain: float
    actual_gain: float = 0.0
    applied: bool = False
    timestamp: float = field(default_factory=time.time)


@dataclass
class SystemSnapshot:
    snapshot_id: str
    performance_score: float
    parameters: dict[str, float]
    timestamp: float = field(default_factory=time.time)


class SelfImprovingAgent:
    def __init__(self, initial_params: dict[str, float] | None = None) -> None:
        self._params: dict[str, float] = initial_params or {
            "learning_rate": 0.01,
            "exploration": 0.3,
            "memory_capacity": 1000.0,
        }
        self._performance_history: list[float] = []
        self._snapshots: list[SystemSnapshot] = []
        self._improvements: list[ImprovementAction] = []
        self._generation = 0

    def evaluate(self, performance: float) -> None:
        self._performance_history.append(performance)
        self._snapshots.append(SystemSnapshot(
            snapshot_id=f"snap_{self._generation}",
            performance_score=performance,
            parameters=dict(self._params),
        ))

    def propose_improvements(self) -> list[ImprovementAction]:
        if len(self._performance_history) < 3:
            return []
        recent = self._performance_history[-3:]
        avg = sum(recent) / len(recent)
        trend = recent[-1] - recent[0]
        actions: list[ImprovementAction] = []
        if trend < 0 or avg < 0.5:
            actions.append(ImprovementAction(
                action_id=f"tune_{self._generation}",
                improvement_type=ImprovementType.PARAMETER_TUNING,
                description="Reduce learning_rate by 10%",
                expected_gain=0.05,
            ))
        if avg > 0.7:
            actions.append(ImprovementAction(
                action_id=f"exploit_{self._generation}",
                improvement_type=ImprovementType.STRATEGY_SWITCH,
                description="Reduce exploration",
                expected_gain=0.03,
            ))
        return actions

    def apply_improvement(self, action: ImprovementAction) -> float:
        if action.improvement_type == ImprovementType.PARAMETER_TUNING:
            self._params["learning_rate"] *= 0.9
        elif action.improvement_type == ImprovementType.STRATEGY_SWITCH:
            self._params["exploration"] = max(0.05, self._params["exploration"] * 0.8)
        action.applied = True
        action.actual_gain = action.expected_gain * 0.85
        self._improvements.append(action)
        self._generation += 1
        return action.actual_gain

    def improvement_summary(self) -> dict[str, Any]:
        applied = [a for a in self._improvements if a.applied]
        return {
            "generation": self._generation,
            "evaluations": len(self._performance_history),
            "improvements_applied": len(applied),
            "total_gain": round(sum(a.actual_gain for a in applied), 4),
            "current_params": dict(self._params),
        }
