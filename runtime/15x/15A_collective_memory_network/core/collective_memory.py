"""15A — Collective Memory Network: Shared Memory Bus + Consensus"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import hashlib
import time
import uuid


@dataclass
class MemoryFragment:
    fragment_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    content: str = ""
    author_agent: str = ""
    importance: float = 0.5
    created_at: float = field(default_factory=time.time)
    consensus_votes: int = 0
    consensus_threshold: int = 3
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def content_hash(self) -> str:
        return hashlib.sha256(self.content.encode()).hexdigest()[:16]

    def is_consensus(self) -> bool:
        return self.consensus_votes >= self.consensus_threshold


class CollectiveMemoryNetwork:
    """Shared memory layer across all STARCORE agents."""

    def __init__(self, consensus_threshold: int = 3) -> None:
        self._fragments: dict[str, MemoryFragment] = {}
        self._agent_index: dict[str, list[str]] = {}
        self._tag_index: dict[str, list[str]] = {}
        self._consensus_threshold = consensus_threshold

    def write(self, content: str, author: str, importance: float = 0.5,
              tags: list[str] | None = None) -> MemoryFragment:
        frag = MemoryFragment(
            content=content,
            author_agent=author,
            importance=importance,
            consensus_threshold=self._consensus_threshold,
            tags=tags or [],
        )
        self._fragments[frag.fragment_id] = frag
        self._agent_index.setdefault(author, []).append(frag.fragment_id)
        for tag in frag.tags:
            self._tag_index.setdefault(tag, []).append(frag.fragment_id)
        return frag

    def vote(self, fragment_id: str, voter_agent: str) -> bool:
        frag = self._fragments.get(fragment_id)
        if not frag:
            return False
        if voter_agent == frag.author_agent:
            return False  # authors cannot vote on their own fragments
        frag.consensus_votes += 1
        return True

    def recall(self, query: str, tag: str | None = None,
               consensus_only: bool = False) -> list[MemoryFragment]:
        candidates: list[MemoryFragment]
        if tag:
            ids = self._tag_index.get(tag, [])
            candidates = [self._fragments[i] for i in ids if i in self._fragments]
        else:
            candidates = list(self._fragments.values())

        if query:
            candidates = [f for f in candidates if query.lower() in f.content.lower()]
        if consensus_only:
            candidates = [f for f in candidates if f.is_consensus()]

        return sorted(candidates, key=lambda f: (f.is_consensus(), f.importance), reverse=True)

    def cross_agent_sync(self, source_agent: str, target_agent: str) -> int:
        """Propagate source agent's high-importance memories to target's index."""
        source_ids = self._agent_index.get(source_agent, [])
        synced = 0
        for fid in source_ids:
            frag = self._fragments.get(fid)
            if frag and frag.importance >= 0.8:
                self._agent_index.setdefault(target_agent, [])
                if fid not in self._agent_index[target_agent]:
                    self._agent_index[target_agent].append(fid)
                    synced += 1
        return synced

    def network_stats(self) -> dict[str, Any]:
        consensus_count = sum(1 for f in self._fragments.values() if f.is_consensus())
        return {
            "total_fragments": len(self._fragments),
            "consensus_fragments": consensus_count,
            "agents": len(self._agent_index),
            "tags": len(self._tag_index),
        }
