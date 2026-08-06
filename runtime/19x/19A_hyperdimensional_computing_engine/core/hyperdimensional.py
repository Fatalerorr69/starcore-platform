"""19A — Hyperdimensional Computing Engine: VSA with binary hypervectors."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import random

_DEFAULT_DIM = 1024


@dataclass
class HyperVector:
    name: str
    bits: list[int] = field(default_factory=list)
    _dim: int = field(default=_DEFAULT_DIM, repr=False)

    def __post_init__(self) -> None:
        if not self.bits:
            self.bits = [random.randint(0, 1) for _ in range(self._dim)]

    def bind(self, other: "HyperVector") -> "HyperVector":
        """XOR: orthogonal to both operands."""
        return HyperVector(
            name=f"{self.name}*{other.name}",
            bits=[a ^ b for a, b in zip(self.bits, other.bits)],
        )

    def similarity(self, other: "HyperVector") -> float:
        """Fraction of matching bits (1.0 = identical, ~0.5 = random)."""
        n = min(len(self.bits), len(other.bits))
        if n == 0:
            return 0.0
        return sum(1 for a, b in zip(self.bits[:n], other.bits[:n]) if a == b) / n

    @staticmethod
    def superpose(*hvs: "HyperVector") -> "HyperVector":
        """Majority-vote bundle of multiple hypervectors."""
        n = min(len(hv.bits) for hv in hvs)
        result = []
        for i in range(n):
            votes = sum(hv.bits[i] for hv in hvs)
            result.append(1 if votes * 2 >= len(hvs) else 0)
        return HyperVector(name="superposed", bits=result)


class HyperdimensionalComputer:
    def __init__(self, dim: int = _DEFAULT_DIM) -> None:
        self._dim = dim
        self._memory: dict[str, HyperVector] = {}
        self._ops: int = 0

    def encode(self, name: str) -> HyperVector:
        if name not in self._memory:
            self._memory[name] = HyperVector(name=name, _dim=self._dim)
        return self._memory[name]

    def query(self, hv: HyperVector, top_k: int = 3) -> list[tuple[str, float]]:
        sims = [(nm, hv.similarity(stored)) for nm, stored in self._memory.items()]
        self._ops += 1
        return sorted(sims, key=lambda x: x[1], reverse=True)[:top_k]

    def compute_stats(self) -> dict[str, Any]:
        return {"dim": self._dim, "stored": len(self._memory), "ops": self._ops}
