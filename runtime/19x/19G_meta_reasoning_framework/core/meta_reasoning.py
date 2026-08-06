"""19G — Meta-Reasoning Framework: strategy-aware cognitive trace evaluation."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ReasoningStrategy(str, Enum):
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"
    PROBABILISTIC = "probabilistic"


STRATEGY_BASE_SCORES: dict[ReasoningStrategy, float] = {
    ReasoningStrategy.DEDUCTIVE: 0.90,
    ReasoningStrategy.PROBABILISTIC: 0.80,
    ReasoningStrategy.INDUCTIVE: 0.70,
    ReasoningStrategy.ABDUCTIVE: 0.60,
    ReasoningStrategy.ANALOGICAL: 0.50,
}


@dataclass
class ReasoningTrace:
    trace_id: str
    strategy: ReasoningStrategy
    premises: list[str] = field(default_factory=list)
    conclusion: str = ""
    confidence: float = 0.0

    def evaluate(self) -> float:
        base = STRATEGY_BASE_SCORES[self.strategy]
        self.confidence = base * min(1.0, len(self.premises) / 3.0)
        return self.confidence


class MetaReasoningFramework:
    def __init__(self) -> None:
        self._traces: list[ReasoningTrace] = []
        self._strategy_usage: dict[str, int] = {s.value: 0 for s in ReasoningStrategy}
        self._meta_confidence: float = 0.0

    def reason(self, trace: ReasoningTrace) -> ReasoningTrace:
        trace.evaluate()
        self._traces.append(trace)
        self._strategy_usage[trace.strategy.value] += 1
        self._meta_confidence = (sum(t.confidence for t in self._traces) /
                                  len(self._traces))
        return trace

    def best_strategy(self) -> ReasoningStrategy:
        return max(STRATEGY_BASE_SCORES, key=lambda s: STRATEGY_BASE_SCORES[s])

    def framework_stats(self) -> dict[str, Any]:
        return {
            "traces": len(self._traces),
            "meta_confidence": round(self._meta_confidence, 4),
            "strategy_usage": dict(self._strategy_usage),
        }
