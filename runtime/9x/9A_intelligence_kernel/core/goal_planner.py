"""9A — Intelligence Kernel: Goal Planner"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlanStep:
    action: str
    preconditions: list[str] = field(default_factory=list)
    effects: list[str] = field(default_factory=list)
    cost: float = 1.0


class GoalPlanner:
    def __init__(self) -> None:
        self._actions: dict[str, PlanStep] = {}
        self._world_state: set[str] = set()

    def register_action(self, step: PlanStep) -> None:
        self._actions[step.action] = step

    def set_world_state(self, facts: set[str]) -> None:
        self._world_state = facts

    def plan_to_goal(self, goal_fact: str) -> list[PlanStep]:
        if goal_fact in self._world_state:
            return []
        applicable = [
            s for s in self._actions.values()
            if all(pre in self._world_state for pre in s.preconditions)
            and goal_fact in s.effects
        ]
        return sorted(applicable, key=lambda s: s.cost)
