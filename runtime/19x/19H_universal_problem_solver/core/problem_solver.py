"""19H — Universal Problem Solver: A* search with pluggable expand/heuristic."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
import heapq


@dataclass
class ProblemState:
    state_id: str
    data: dict[str, Any] = field(default_factory=dict)
    cost: float = 0.0

    def __lt__(self, other: "ProblemState") -> bool:
        return self.cost < other.cost


@dataclass
class Solution:
    found: bool
    path: list[str]
    total_cost: float
    iterations: int


class UniversalProblemSolver:
    def __init__(self, max_iterations: int = 1000) -> None:
        self._max_iter = max_iterations
        self._solves: int = 0

    def solve(
        self,
        initial: ProblemState,
        is_goal: Callable[[ProblemState], bool],
        expand: Callable[[ProblemState], list[ProblemState]],
        heuristic: Callable[[ProblemState], float] | None = None,
    ) -> Solution:
        open_set: list[tuple[float, ProblemState]] = [(0.0, initial)]
        visited: set[str] = set()
        parents: dict[str, str] = {}
        cost_so_far: dict[str, float] = {initial.state_id: 0.0}
        iterations = 0

        while open_set and iterations < self._max_iter:
            _, current = heapq.heappop(open_set)
            iterations += 1
            if current.state_id in visited:
                continue
            visited.add(current.state_id)

            if is_goal(current):
                path: list[str] = []
                cid = current.state_id
                while cid:
                    path.append(cid)
                    cid = parents.get(cid, "")
                self._solves += 1
                return Solution(
                    found=True,
                    path=list(reversed(path)),
                    total_cost=cost_so_far.get(current.state_id, 0.0),
                    iterations=iterations,
                )

            for neighbor in expand(current):
                if neighbor.state_id not in visited:
                    new_cost = cost_so_far.get(current.state_id, 0.0) + neighbor.cost
                    if (neighbor.state_id not in cost_so_far or
                            new_cost < cost_so_far[neighbor.state_id]):
                        cost_so_far[neighbor.state_id] = new_cost
                        parents[neighbor.state_id] = current.state_id
                        h = heuristic(neighbor) if heuristic else 0.0
                        heapq.heappush(open_set, (new_cost + h, neighbor))

        self._solves += 1
        return Solution(found=False, path=[], total_cost=float("inf"),
                        iterations=iterations)

    def solver_stats(self) -> dict[str, Any]:
        return {"solves": self._solves, "max_iterations": self._max_iter}
