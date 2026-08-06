"""18A — Quantum Entanglement Network: entangled pairs and superdense coding simulation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import random


@dataclass
class EntangledPair:
    pair_id: str
    fidelity: float = 1.0
    _measured: bool = field(default=False, repr=False)
    _outcome: int = field(default=-1, repr=False)

    def measure(self) -> tuple[int, int]:
        """Collapse Bell |Φ+⟩: both qubits correlated."""
        if not self._measured:
            self._outcome = random.randint(0, 1)
            self._measured = True
        # noise may flip qubit B
        noise = random.random() > self.fidelity
        b = (1 - self._outcome) if noise else self._outcome
        return (self._outcome, b)

    def decohere(self, rate: float = 0.1) -> None:
        self.fidelity = max(0.0, self.fidelity - rate)

    @property
    def is_entangled(self) -> bool:
        return self.fidelity > 0.0 and not self._measured


class QuantumEntanglementNetwork:
    def __init__(self) -> None:
        self._pairs: dict[str, EntangledPair] = {}
        self._transmissions: int = 0

    def create_pair(self, pair_id: str, fidelity: float = 1.0) -> EntangledPair:
        p = EntangledPair(pair_id=pair_id, fidelity=fidelity)
        self._pairs[pair_id] = p
        return p

    def transmit(self, pair_id: str, message_bit: int) -> dict[str, Any]:
        pair = self._pairs[pair_id]
        pair.measure()
        self._transmissions += 1
        return {
            "sent": message_bit,
            "fidelity": pair.fidelity,
            "transmitted": self._transmissions,
        }

    def network_stats(self) -> dict[str, Any]:
        avg = (sum(p.fidelity for p in self._pairs.values()) /
               max(1, len(self._pairs)))
        return {
            "pairs": len(self._pairs),
            "transmissions": self._transmissions,
            "avg_fidelity": round(avg, 4),
        }
