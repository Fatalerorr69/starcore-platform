"""19E — Distributed Wisdom Network: reliability-weighted knowledge aggregation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class WisdomNode:
    node_id: str
    expertise: str
    knowledge: dict[str, float] = field(default_factory=dict)
    reliability: float = 1.0

    def contribute(self, topic: str, value: float) -> None:
        self.knowledge[topic] = value


class DistributedWisdomNetwork:
    def __init__(self) -> None:
        self._nodes: dict[str, WisdomNode] = {}
        self._consensus_cache: dict[str, float] = {}
        self._queries: int = 0

    def add_node(self, node: WisdomNode) -> None:
        self._nodes[node.node_id] = node

    def aggregate(self, topic: str) -> float:
        """Reliability-weighted average across nodes that know the topic."""
        total_weight = 0.0
        weighted_sum = 0.0
        for node in self._nodes.values():
            if topic in node.knowledge:
                w = node.reliability
                weighted_sum += node.knowledge[topic] * w
                total_weight += w
        if total_weight < 1e-9:
            return 0.0
        result = weighted_sum / total_weight
        self._consensus_cache[topic] = result
        self._queries += 1
        return result

    def network_wisdom(self, topics: list[str]) -> dict[str, float]:
        return {t: self.aggregate(t) for t in topics}

    def network_stats(self) -> dict[str, Any]:
        return {
            "nodes": len(self._nodes),
            "cached_topics": len(self._consensus_cache),
            "queries": self._queries,
        }
