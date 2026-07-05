"""
Task Graph
"""

from collections import defaultdict

from .task import Task


class TaskGraph:

    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}
        self.edges = defaultdict(set)

    def add_task(self, task: Task) -> None:
        self.tasks[task.id] = task

        for dependency in task.depends_on:
            self.edges[dependency].add(task.id)

    def get(self, task_id: str) -> Task:
        return self.tasks[task_id]

    def all(self):
        return self.tasks.values()
