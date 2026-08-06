"""9D — AI Research Engine"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import uuid


class ExperimentStatus(str, Enum):
    PROPOSED = "proposed"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass
class Hypothesis:
    statement: str
    confidence: float = 0.5
    evidence_for: list[str] = field(default_factory=list)
    evidence_against: list[str] = field(default_factory=list)

    def update(self, evidence: str, supports: bool) -> None:
        if supports:
            self.evidence_for.append(evidence)
            self.confidence = min(0.99, self.confidence + 0.05)
        else:
            self.evidence_against.append(evidence)
            self.confidence = max(0.01, self.confidence - 0.05)


@dataclass
class Experiment:
    experiment_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    hypothesis: Hypothesis | None = None
    methodology: str = ""
    results: dict[str, Any] = field(default_factory=dict)
    status: ExperimentStatus = ExperimentStatus.PROPOSED


class ResearchEngine:
    def __init__(self) -> None:
        self._hypotheses: list[Hypothesis] = []
        self._experiments: dict[str, Experiment] = {}

    def propose(self, statement: str) -> Hypothesis:
        h = Hypothesis(statement=statement)
        self._hypotheses.append(h)
        return h

    def design_experiment(self, hypothesis: Hypothesis, methodology: str) -> Experiment:
        exp = Experiment(hypothesis=hypothesis, methodology=methodology)
        self._experiments[exp.experiment_id] = exp
        return exp

    def run_experiment(self, exp_id: str, results: dict[str, Any]) -> Experiment:
        exp = self._experiments.get(exp_id)
        if not exp:
            raise KeyError(f"Experiment {exp_id} not found")
        exp.status = ExperimentStatus.RUNNING
        exp.results = results
        exp.status = ExperimentStatus.COMPLETED
        if exp.hypothesis and "success" in results:
            exp.hypothesis.update("experiment result", results["success"])
        return exp

    def top_hypotheses(self, n: int = 5) -> list[Hypothesis]:
        return sorted(self._hypotheses, key=lambda h: h.confidence, reverse=True)[:n]
