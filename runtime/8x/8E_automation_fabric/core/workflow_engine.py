"""8E — Automation Fabric: Workflow Engine"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    name: str
    action: Callable[..., Any]
    depends_on: list[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING


@dataclass
class Workflow:
    name: str
    steps: list[WorkflowStep] = field(default_factory=list)

    def add_step(self, step: WorkflowStep) -> None:
        self.steps.append(step)

    def execute(self) -> dict[str, StepStatus]:
        completed: set[str] = set()
        results: dict[str, StepStatus] = {}

        for step in self.steps:
            if all(dep in completed for dep in step.depends_on):
                try:
                    step.action()
                    step.status = StepStatus.COMPLETED
                    completed.add(step.name)
                except Exception:
                    step.status = StepStatus.FAILED
            else:
                step.status = StepStatus.SKIPPED
            results[step.name] = step.status

        return results
