"""17H — Causal Intervention Engine: do-calculus with graph surgery."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from collections import deque
import time


class EdgeType(str, Enum):
    DIRECT = "direct"
    MEDIATED = "mediated"
    CONFOUNDED = "confounded"


@dataclass
class CausalVariable:
    var_id: str
    name: str
    value: float = 0.0
    observed: bool = True


@dataclass
class CausalEdge:
    source: str
    target: str
    strength: float = 1.0
    edge_type: EdgeType = EdgeType.DIRECT


@dataclass
class InterventionResult:
    do_variable: str
    do_value: float
    effects: dict[str, float]
    timestamp: float = field(default_factory=time.time)


class CausalInterventionEngine:
    def __init__(self) -> None:
        self._variables: dict[str, CausalVariable] = {}
        self._edges: list[CausalEdge] = []
        self._adjacency: dict[str, list[tuple[str, float]]] = {}
        self._interventions: list[InterventionResult] = []

    def add_variable(self, var: CausalVariable) -> None:
        self._variables[var.var_id] = var
        self._adjacency.setdefault(var.var_id, [])

    def add_edge(self, edge: CausalEdge) -> None:
        self._edges.append(edge)
        self._adjacency.setdefault(edge.source, []).append((edge.target, edge.strength))

    def intervene(self, do_var: str, do_value: float) -> InterventionResult:
        if do_var not in self._variables:
            return InterventionResult(do_var, do_value, {})
        self._variables[do_var].value = do_value
        effects: dict[str, float] = {}
        queue: deque[str] = deque([do_var])
        visited: set[str] = {do_var}
        while queue:
            current = queue.popleft()
            cur_val = self._variables[current].value
            for (target, strength) in self._adjacency.get(current, []):
                if target not in visited:
                    effect = cur_val * strength
                    self._variables[target].value = effect
                    effects[target] = effect
                    queue.append(target)
                    visited.add(target)
        result = InterventionResult(do_var, do_value,
                                    {k: v for k, v in effects.items() if k != do_var})
        self._interventions.append(result)
        return result

    def counterfactual(self, do_var: str, do_value: float, query_var: str) -> tuple[float, float]:
        factual_val = self._variables.get(query_var, CausalVariable("", "")).value
        result = self.intervene(do_var, do_value)
        cf_val = result.effects.get(query_var, factual_val)
        return (factual_val, cf_val)

    def causal_path(self, source: str, target: str) -> list[str]:
        if source not in self._variables or target not in self._variables:
            return []
        visited: set[str] = {source}
        queue: deque[list[str]] = deque([[source]])
        while queue:
            path = queue.popleft()
            if path[-1] == target:
                return path
            for (nb, _) in self._adjacency.get(path[-1], []):
                if nb not in visited:
                    visited.add(nb)
                    queue.append(path + [nb])
        return []

    def engine_stats(self) -> dict[str, Any]:
        return {"variables": len(self._variables), "edges": len(self._edges),
                "interventions": len(self._interventions)}
