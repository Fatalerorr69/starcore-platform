"""9C — Long Term Memory Fabric"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time
import math


class MemoryType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


@dataclass
class MemoryTrace:
    content: str
    memory_type: MemoryType
    importance: float = 0.5
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def strength(self) -> float:
        age_hours = (time.time() - self.created_at) / 3600
        decay = math.exp(-0.1 * age_hours)
        return self.importance * decay * (1 + math.log1p(self.access_count))


class LongTermMemory:
    def __init__(self, capacity: int = 10_000) -> None:
        self._traces: list[MemoryTrace] = []
        self._capacity = capacity

    def store(self, trace: MemoryTrace) -> None:
        self._traces.append(trace)
        if len(self._traces) > self._capacity:
            self._consolidate()

    def recall(self, query: str, memory_type: MemoryType | None = None,
               top_k: int = 10) -> list[MemoryTrace]:
        candidates = [
            t for t in self._traces
            if query.lower() in t.content.lower()
            and (memory_type is None or t.memory_type == memory_type)
        ]
        for t in candidates:
            t.access_count += 1
            t.last_accessed = time.time()
        return sorted(candidates, key=lambda t: t.strength(), reverse=True)[:top_k]

    def _consolidate(self) -> None:
        self._traces = sorted(self._traces, key=lambda t: t.strength(), reverse=True)
        self._traces = self._traces[:int(self._capacity * 0.8)]

    def stats(self) -> dict[str, Any]:
        return {
            "total_traces": len(self._traces),
            "capacity": self._capacity,
            "episodic": sum(1 for t in self._traces if t.memory_type == MemoryType.EPISODIC),
            "semantic": sum(1 for t in self._traces if t.memory_type == MemoryType.SEMANTIC),
            "procedural": sum(1 for t in self._traces if t.memory_type == MemoryType.PROCEDURAL),
        }
