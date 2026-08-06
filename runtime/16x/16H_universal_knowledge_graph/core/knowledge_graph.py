"""16H — Universal Knowledge Graph: Concept graph with semantic similarity."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from collections import deque
import time


@dataclass
class Concept:
    concept_id: str
    name: str
    description: str = ""
    embedding: list[float] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass
class Relation:
    relation_id: str
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


class KnowledgeGraph:
    def __init__(self) -> None:
        self._concepts: dict[str, Concept] = {}
        self._relations: list[Relation] = []
        self._adjacency: dict[str, list[tuple[str, str, float]]] = {}

    def add_concept(self, concept: Concept) -> None:
        self._concepts[concept.concept_id] = concept
        if concept.concept_id not in self._adjacency:
            self._adjacency[concept.concept_id] = []

    def add_relation(self, relation: Relation) -> None:
        self._relations.append(relation)
        if relation.source_id not in self._adjacency:
            self._adjacency[relation.source_id] = []
        self._adjacency[relation.source_id].append(
            (relation.target_id, relation.relation_type, relation.weight))

    def shortest_path(self, source_id: str, target_id: str) -> list[str]:
        if source_id not in self._concepts or target_id not in self._concepts:
            return []
        visited: set[str] = {source_id}
        queue: deque[list[str]] = deque([[source_id]])
        while queue:
            path = queue.popleft()
            node = path[-1]
            if node == target_id:
                return path
            for neighbor, _, _ in self._adjacency.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        return []

    def neighbors(self, concept_id: str, relation_type: str | None = None) -> list[str]:
        return [tid for (tid, rtype, _) in self._adjacency.get(concept_id, [])
                if relation_type is None or rtype == relation_type]

    def semantic_similarity(self, id_a: str, id_b: str) -> float:
        a = self._concepts.get(id_a)
        b = self._concepts.get(id_b)
        if not a or not b or not a.embedding or not b.embedding:
            return 0.0
        min_len = min(len(a.embedding), len(b.embedding))
        dot = sum(a.embedding[i] * b.embedding[i] for i in range(min_len))
        norm_a = sum(x ** 2 for x in a.embedding) ** 0.5
        norm_b = sum(x ** 2 for x in b.embedding) ** 0.5
        if norm_a < 1e-9 or norm_b < 1e-9:
            return 0.0
        return dot / (norm_a * norm_b)

    def graph_stats(self) -> dict[str, Any]:
        avg_deg = (sum(len(v) for v in self._adjacency.values())
                   / max(1, len(self._adjacency)))
        return {"concepts": len(self._concepts),
                "relations": len(self._relations),
                "avg_degree": round(avg_deg, 4)}
