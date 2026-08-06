"""16E — Quantum Coherence Network: Entanglement-based communication simulation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import math
import random
import time


@dataclass
class QuantumState:
    n_qubits: int
    amplitudes: list[complex] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.amplitudes:
            size = 2 ** self.n_qubits
            self.amplitudes = [complex(0)] * size
            self.amplitudes[0] = complex(1)

    def norm(self) -> float:
        return math.sqrt(sum(abs(a) ** 2 for a in self.amplitudes))

    def normalize(self) -> None:
        n = self.norm()
        if n > 1e-9:
            self.amplitudes = [a / n for a in self.amplitudes]

    def measure(self) -> int:
        probs = [abs(a) ** 2 for a in self.amplitudes]
        r = random.random()
        cumulative = 0.0
        for i, p in enumerate(probs):
            cumulative += p
            if r <= cumulative:
                return i
        return len(probs) - 1


@dataclass
class EntangledPair:
    pair_id: str
    qubit_a: int
    qubit_b: int
    fidelity: float = 1.0
    created_at: float = field(default_factory=time.time)

    def decohere(self, rate: float = 0.01) -> None:
        self.fidelity = max(0.0, self.fidelity - rate)


class QuantumCoherenceNetwork:
    def __init__(self) -> None:
        self._states: dict[str, QuantumState] = {}
        self._pairs: dict[str, EntangledPair] = {}
        self._decoherence_rate = 0.005

    def create_bell_state(self, state_id: str) -> QuantumState:
        """Create |Φ+⟩ = (|00⟩ + |11⟩)/√2"""
        inv_sqrt2 = 1.0 / math.sqrt(2)
        state = QuantumState(n_qubits=2)
        state.amplitudes = [complex(inv_sqrt2), complex(0), complex(0), complex(inv_sqrt2)]
        self._states[state_id] = state
        return state

    def entangle(self, pair_id: str, qubit_a: int, qubit_b: int) -> EntangledPair:
        pair = EntangledPair(pair_id=pair_id, qubit_a=qubit_a, qubit_b=qubit_b)
        self._pairs[pair_id] = pair
        return pair

    def tick_decoherence(self) -> None:
        for pair in self._pairs.values():
            pair.decohere(self._decoherence_rate)

    def teleport(self, pair_id: str, value: float) -> float | None:
        pair = self._pairs.get(pair_id)
        if not pair or pair.fidelity < 0.5:
            return None
        noise = (1.0 - pair.fidelity) * random.gauss(0, 0.1)
        return value + noise

    def network_health(self) -> dict[str, Any]:
        if not self._pairs:
            return {"pairs": 0, "avg_fidelity": 0.0, "usable_pairs": 0}
        avg_fidelity = sum(p.fidelity for p in self._pairs.values()) / len(self._pairs)
        usable = sum(1 for p in self._pairs.values() if p.fidelity >= 0.5)
        return {"pairs": len(self._pairs),
                "avg_fidelity": round(avg_fidelity, 4),
                "usable_pairs": usable}
