"""18F — Multi-Agent Coordination Hub: priority-aware task allocation."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentRole(str, Enum):
    WORKER = "worker"
    COORDINATOR = "coordinator"
    OBSERVER = "observer"


class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class CoordinationTask:
    task_id: str
    description: str
    priority: int = 5
    required_capacity: float = 1.0
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: str = ""


@dataclass
class CoordinationAgent:
    agent_id: str
    role: AgentRole = AgentRole.WORKER
    capacity: float = 1.0
    load: float = 0.0
    tasks_completed: int = 0

    @property
    def available_capacity(self) -> float:
        return max(0.0, self.capacity - self.load)

    def assign_task(self, task: CoordinationTask) -> bool:
        if self.available_capacity >= task.required_capacity:
            self.load += task.required_capacity
            task.status = TaskStatus.ASSIGNED
            task.assigned_to = self.agent_id
            return True
        return False

    def complete_task(self, task: CoordinationTask) -> None:
        self.load = max(0.0, self.load - task.required_capacity)
        task.status = TaskStatus.COMPLETED
        self.tasks_completed += 1


class CoordinationHub:
    def __init__(self) -> None:
        self._agents: dict[str, CoordinationAgent] = {}
        self._tasks: dict[str, CoordinationTask] = {}
        self._rounds: int = 0

    def register_agent(self, agent: CoordinationAgent) -> None:
        self._agents[agent.agent_id] = agent

    def submit_task(self, task: CoordinationTask) -> None:
        self._tasks[task.task_id] = task

    def allocate(self) -> dict[str, str]:
        assignments: dict[str, str] = {}
        pending = sorted(
            [t for t in self._tasks.values() if t.status == TaskStatus.PENDING],
            key=lambda t: t.priority,
        )
        workers = [a for a in self._agents.values() if a.role == AgentRole.WORKER]
        for task in pending:
            candidates = [w for w in workers if w.available_capacity >= task.required_capacity]
            if candidates:
                chosen = min(candidates, key=lambda w: w.load)
                if chosen.assign_task(task):
                    assignments[task.task_id] = chosen.agent_id
        self._rounds += 1
        return assignments

    def hub_stats(self) -> dict[str, Any]:
        completed = sum(1 for t in self._tasks.values() if t.status == TaskStatus.COMPLETED)
        return {
            "agents": len(self._agents),
            "tasks": len(self._tasks),
            "completed": completed,
            "rounds": self._rounds,
        }
