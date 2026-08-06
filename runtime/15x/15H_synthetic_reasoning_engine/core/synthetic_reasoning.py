"""15H — Synthetic Reasoning Engine: Causal Graph + Counterfactual Engine"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from collections import defaultdict, deque


@dataclass
class CausalNode:
    name: str
    value: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CausalEdge:
    cause: str
    effect: str
    strength: float = 1.0  # 0–1 causal strength
    mechanism: str = ""


@dataclass
class Counterfactual:
    intervention: dict[str, Any]
    original_outcome: dict[str, Any]
    counterfactual_outcome: dict[str, Any]
    difference: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for key in self.original_outcome:
            orig = self.original_outcome[key]
            cfact = self.counterfactual_outcome.get(key)
            if orig != cfact:
                self.difference[key] = {"was": orig, "would_be": cfact}


class CausalGraph:
    """Directed causal graph supporting do-calculus style interventions."""

    def __init__(self) -> None:
        self._nodes: dict[str, CausalNode] = {}
        self._edges: list[CausalEdge] = []
        self._adj: dict[str, list[str]] = defaultdict(list)
        self._rev_adj: dict[str, list[str]] = defaultdict(list)

    def add_node(self, node: CausalNode) -> None:
        self._nodes[node.name] = node

    def add_edge(self, edge: CausalEdge) -> None:
        self._edges.append(edge)
        self._adj[edge.cause].append(edge.effect)
        self._rev_adj[edge.effect].append(edge.cause)

    def causes_of(self, node_name: str) -> list[str]:
        return list(self._rev_adj.get(node_name, []))

    def effects_of(self, node_name: str) -> list[str]:
        return list(self._adj.get(node_name, []))

    def causal_path(self, source: str, target: str) -> list[str] | None:
        """BFS shortest causal path from source to target."""
        if source not in self._nodes or target not in self._nodes:
            return None
        queue: deque[list[str]] = deque([[source]])
        visited: set[str] = {source}
        while queue:
            path = queue.popleft()
            current = path[-1]
            if current == target:
                return path
            for neighbor in self._adj.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        return None

    def intervene(self, node_name: str, new_value: Any) -> dict[str, Any]:
        """do(X=v): set node value and propagate to descendants."""
        if node_name not in self._nodes:
            return {}
        node = self._nodes[node_name]
        old_value = node.value
        node.value = new_value
        propagated: dict[str, Any] = {node_name: new_value}

        queue: deque[str] = deque(self._adj.get(node_name, []))
        visited: set[str] = {node_name}
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            causes = self._rev_adj.get(current, [])
            total = sum(
                (self._nodes[c].value or 0) * e.strength
                for e in self._edges if e.effect == current and e.cause in self._nodes
                for c in [e.cause]
            )
            self._nodes[current].value = total
            propagated[current] = total
            for child in self._adj.get(current, []):
                if child not in visited:
                    queue.append(child)

        node.value = old_value  # restore (do-calculus: we only query, not commit)
        return propagated

    def counterfactual(self, intervention: dict[str, Any],
                       outcome_nodes: list[str]) -> Counterfactual:
        original = {n: self._nodes[n].value for n in outcome_nodes if n in self._nodes}
        cf_outcome: dict[str, Any] = {}
        for node_name, value in intervention.items():
            propagated = self.intervene(node_name, value)
            for n in outcome_nodes:
                if n in propagated:
                    cf_outcome[n] = propagated[n]
        for n in outcome_nodes:
            if n not in cf_outcome:
                cf_outcome[n] = original.get(n)
        return Counterfactual(
            intervention=intervention,
            original_outcome=original,
            counterfactual_outcome=cf_outcome,
        )
