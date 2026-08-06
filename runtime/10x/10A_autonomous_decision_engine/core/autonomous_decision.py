"""STARCORE 10A — Autonomous Decision Engine"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import math


@dataclass
class Action:
    name: str
    expected_reward: float
    cost: float
    probability: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def utility(self) -> float:
        return self.probability * self.expected_reward - self.cost


@dataclass
class DecisionContext:
    state: dict[str, Any]
    available_actions: list[Action] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)


class AutonomousDecisionEngine:
    def __init__(self, discount_factor: float = 0.95) -> None:
        self._discount = discount_factor
        self._history: list[tuple[DecisionContext, Action]] = []

    def decide(self, context: DecisionContext) -> Action | None:
        if not context.available_actions:
            return None
        valid = [a for a in context.available_actions if self._satisfies_constraints(a, context)]
        if not valid:
            return None
        best = max(valid, key=lambda a: a.utility())
        self._history.append((context, best))
        return best

    def _satisfies_constraints(self, action: Action, ctx: DecisionContext) -> bool:
        max_cost = ctx.constraints.get("max_cost")
        if max_cost is not None and action.cost > max_cost:
            return False
        min_prob = ctx.constraints.get("min_probability")
        if min_prob is not None and action.probability < min_prob:
            return False
        return True

    def update_rewards(self, action_name: str, actual_reward: float) -> None:
        for ctx, action in reversed(self._history):
            if action.name == action_name:
                alpha = 0.1
                action.expected_reward = (1 - alpha) * action.expected_reward + alpha * actual_reward
                break

    def stats(self) -> dict[str, Any]:
        return {"decisions_made": len(self._history), "discount_factor": self._discount}
