"""18D — Universal Language Bridge: hash-embedding concept translation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import hashlib
import math


@dataclass
class ConceptVector:
    concept: str
    embedding: list[float] = field(default_factory=list)
    language: str = "universal"

    def __post_init__(self) -> None:
        if not self.embedding:
            h = hashlib.sha256(self.concept.encode()).digest()
            self.embedding = [(b / 127.5) - 1.0 for b in h[:16]]

    @property
    def norm(self) -> float:
        return math.sqrt(sum(x * x for x in self.embedding))

    def similarity(self, other: "ConceptVector") -> float:
        n = min(len(self.embedding), len(other.embedding))
        if n == 0:
            return 0.0
        dot = sum(self.embedding[i] * other.embedding[i] for i in range(n))
        denom = self.norm * other.norm
        if denom < 1e-9:
            return 0.0
        return max(-1.0, min(1.0, dot / denom))


class UniversalLanguageBridge:
    def __init__(self) -> None:
        self._concepts: dict[str, ConceptVector] = {}
        self._translations: int = 0

    def register(self, concept: str, language: str = "universal",
                 embedding: list[float] | None = None) -> ConceptVector:
        cv = ConceptVector(concept=concept, language=language,
                           embedding=embedding or [])
        self._concepts[concept] = cv
        return cv

    def translate(self, concept: str, target_language: str) -> dict[str, Any]:
        if concept not in self._concepts:
            self.register(concept)
        cv = self._concepts[concept]
        best_match = concept
        best_sim = -1.0
        for name, other in self._concepts.items():
            if other.language == target_language and name != concept:
                sim = cv.similarity(other)
                if sim > best_sim:
                    best_sim = sim
                    best_match = name
        self._translations += 1
        return {
            "source": concept,
            "target_language": target_language,
            "translation": best_match,
            "confidence": max(0.0, best_sim) if best_sim >= 0.0 else 0.0,
        }

    def similarity(self, a: str, b: str) -> float:
        if a not in self._concepts:
            self.register(a)
        if b not in self._concepts:
            self.register(b)
        return self._concepts[a].similarity(self._concepts[b])

    def bridge_stats(self) -> dict[str, Any]:
        return {"concepts": len(self._concepts), "translations": self._translations}
