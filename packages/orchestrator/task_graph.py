"""
Task Graph
"""

from __future__ import annotations

from collections import defaultdict

from .task import Task


class TaskGraph:
    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}
        self.edges: dict[str, set[str]] = defaultdict(set)

    def add_task(self, task: Task) -> None:
        self.tasks[task.id] = task
        for dependency in task.depends_on:
            self.edges[dependency].add(task.id)

    def get(self, task_id: str) -> Task:
        return self.tasks[task_id]

    def all(self):
        return self.tasks.values()

    def dependents_of(self, task_id: str) -> set[str]:
        return self.edges.get(task_id, set())
