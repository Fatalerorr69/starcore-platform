"""19B — Cognitive Load Balancer: multi-channel task scheduling by cognitive cost."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CognitiveTask:
    task_id: str
    name: str
    priority: TaskPriority = TaskPriority.MEDIUM
    cognitive_cost: float = 0.3
    completed: bool = False


@dataclass
class CognitiveChannel:
    channel_id: str
    max_load: float = 1.0
    current_load: float = 0.0
    tasks: list[CognitiveTask] = field(default_factory=list)

    @property
    def available_capacity(self) -> float:
        return max(0.0, self.max_load - self.current_load)

    def accept(self, task: CognitiveTask) -> bool:
        if self.available_capacity >= task.cognitive_cost:
            self.tasks.append(task)
            self.current_load += task.cognitive_cost
            return True
        return False

    def complete(self, task_id: str) -> bool:
        for t in self.tasks:
            if t.task_id == task_id and not t.completed:
                t.completed = True
                self.current_load = max(0.0, self.current_load - t.cognitive_cost)
                return True
        return False


class CognitiveLoadBalancer:
    def __init__(self, num_channels: int = 3) -> None:
        self._channels = [CognitiveChannel(f"ch_{i}") for i in range(num_channels)]
        self._processed: int = 0

    def submit(self, task: CognitiveTask) -> str | None:
        for ch in sorted(self._channels, key=lambda c: c.available_capacity, reverse=True):
            if ch.accept(task):
                self._processed += 1
                return ch.channel_id
        return None

    def total_load(self) -> float:
        return sum(ch.current_load for ch in self._channels)

    def balancer_stats(self) -> dict[str, Any]:
        return {
            "channels": len(self._channels),
            "total_load": round(self.total_load(), 4),
            "processed": self._processed,
        }
