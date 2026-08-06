"""9A — Intelligence Kernel: Reasoning Engine"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ReasoningMode(str, Enum):
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"


@dataclass
class Belief:
    proposition: str
    confidence: float  # 0.0 – 1.0
    evidence: list[str] = field(default_factory=list)
    mode: ReasoningMode = ReasoningMode.DEDUCTIVE


@dataclass
class Goal:
    description: str
    priority: int = 5
    sub_goals: list["Goal"] = field(default_factory=list)
    achieved: bool = False


class ReasoningEngine:
    def __init__(self) -> None:
        self._beliefs: list[Belief] = []
        self._goals: list[Goal] = []

    def add_belief(self, belief: Belief) -> None:
        self._beliefs.append(belief)

    def add_goal(self, goal: Goal) -> None:
        self._goals.append(goal)

    def infer(self, query: str) -> list[Belief]:
        return [b for b in self._beliefs if query.lower() in b.proposition.lower()]

    def plan(self) -> list[Goal]:
        return sorted(self._goals, key=lambda g: g.priority)

    def update_belief(self, proposition: str, new_confidence: float, evidence: str) -> None:
        for b in self._beliefs:
            if b.proposition == proposition:
                b.confidence = new_confidence
                b.evidence.append(evidence)
                return
        self._beliefs.append(Belief(
            proposition=proposition,
            confidence=new_confidence,
            evidence=[evidence],
            mode=ReasoningMode.INDUCTIVE,
        ))

    def health(self) -> dict[str, Any]:
        return {
            "beliefs": len(self._beliefs),
            "goals": len(self._goals),
            "status": "ok",
        }
