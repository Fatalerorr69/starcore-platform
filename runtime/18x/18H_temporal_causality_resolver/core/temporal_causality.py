"""18H — Temporal Causality Resolver: causal chain consistency and paradox detection."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CausalEvent:
    event_id: str
    timestamp: float
    payload: dict[str, Any] = field(default_factory=dict)
    causes: list[str] = field(default_factory=list)


@dataclass
class CausalChain:
    chain_id: str
    events: list[CausalEvent] = field(default_factory=list)

    def add_event(self, event: CausalEvent) -> None:
        self.events.append(event)
        self.events.sort(key=lambda e: e.timestamp)

    def is_consistent(self) -> bool:
        """Causes must temporally precede effects."""
        id_to_ts = {e.event_id: e.timestamp for e in self.events}
        for event in self.events:
            for cause_id in event.causes:
                if cause_id in id_to_ts:
                    if id_to_ts[cause_id] >= event.timestamp:
                        return False
        return True


class TemporalCausalityResolver:
    def __init__(self) -> None:
        self._chains: dict[str, CausalChain] = {}
        self._events: dict[str, CausalEvent] = {}
        self._resolutions: int = 0

    def record_event(self, event: CausalEvent) -> None:
        self._events[event.event_id] = event

    def create_chain(self, chain_id: str, event_ids: list[str]) -> CausalChain:
        chain = CausalChain(chain_id=chain_id)
        for eid in event_ids:
            if eid in self._events:
                chain.add_event(self._events[eid])
        self._chains[chain_id] = chain
        return chain

    def resolve(self, chain_id: str) -> dict[str, Any]:
        chain = self._chains.get(chain_id)
        if not chain:
            return {"resolved": False, "reason": "chain not found"}
        consistent = chain.is_consistent()
        self._resolutions += 1
        return {
            "chain_id": chain_id,
            "consistent": consistent,
            "events": len(chain.events),
            "paradox": not consistent,
        }

    def detect_paradox(self, chain_id: str) -> bool:
        chain = self._chains.get(chain_id)
        return chain is not None and not chain.is_consistent()

    def resolver_stats(self) -> dict[str, Any]:
        return {
            "events": len(self._events),
            "chains": len(self._chains),
            "resolutions": self._resolutions,
        }
