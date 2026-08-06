"""15F — Quantum Algorithm Bridge: Qubit Simulator & Grover Search"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import math
import cmath
import random


Complex = complex


@dataclass
class Qubit:
    """Single qubit state |ψ⟩ = α|0⟩ + β|1⟩ with normalization constraint."""
    alpha: Complex = complex(1, 0)
    beta: Complex = complex(0, 0)

    def __post_init__(self) -> None:
        self._normalize()

    def _normalize(self) -> None:
        norm = math.sqrt(abs(self.alpha) ** 2 + abs(self.beta) ** 2)
        if norm > 1e-9:
            self.alpha /= norm
            self.beta /= norm

    def apply_hadamard(self) -> "Qubit":
        inv_sqrt2 = 1 / math.sqrt(2)
        new_alpha = inv_sqrt2 * (self.alpha + self.beta)
        new_beta = inv_sqrt2 * (self.alpha - self.beta)
        return Qubit(new_alpha, new_beta)

    def apply_pauli_x(self) -> "Qubit":
        return Qubit(self.beta, self.alpha)

    def apply_phase(self, theta: float) -> "Qubit":
        return Qubit(self.alpha, self.beta * cmath.exp(complex(0, theta)))

    def measure(self) -> int:
        prob_zero = abs(self.alpha) ** 2
        return 0 if random.random() < prob_zero else 1

    def probability(self) -> dict[str, float]:
        return {"p0": abs(self.alpha) ** 2, "p1": abs(self.beta) ** 2}


class GroverSearch:
    """Classical simulation of Grover's quantum search algorithm."""

    def __init__(self, n_qubits: int) -> None:
        self._n = n_qubits
        self._search_space = 2 ** n_qubits

    def optimal_iterations(self) -> int:
        return max(1, round(math.pi / 4 * math.sqrt(self._search_space)))

    def search(self, oracle: Any, iterations: int | None = None) -> tuple[int, float]:
        """
        Simulate Grover's search. oracle(x) -> bool marks the target.
        Returns (found_index, confidence).
        """
        iters = iterations or self.optimal_iterations()
        amplitudes = [1.0 / math.sqrt(self._search_space)] * self._search_space

        for _ in range(iters):
            for i in range(self._search_space):
                if oracle(i):
                    amplitudes[i] *= -1.0
            mean = sum(amplitudes) / len(amplitudes)
            amplitudes = [2 * mean - a for a in amplitudes]

        max_amp = max(amplitudes)
        best_idx = amplitudes.index(max_amp)
        confidence = max_amp ** 2
        return best_idx, confidence

    def speedup_factor(self) -> float:
        classical = float(self._search_space)
        quantum_ops = float(self.optimal_iterations())
        return classical / (quantum_ops * math.log2(self._search_space + 1))


@dataclass
class QuantumCircuit:
    n_qubits: int
    gates: list[dict[str, Any]] = field(default_factory=list)

    def h(self, qubit_idx: int) -> "QuantumCircuit":
        self.gates.append({"gate": "H", "qubit": qubit_idx})
        return self

    def x(self, qubit_idx: int) -> "QuantumCircuit":
        self.gates.append({"gate": "X", "qubit": qubit_idx})
        return self

    def cx(self, control: int, target: int) -> "QuantumCircuit":
        self.gates.append({"gate": "CX", "control": control, "target": target})
        return self

    def depth(self) -> int:
        return len(self.gates)

    def description(self) -> str:
        return f"QuantumCircuit({self.n_qubits} qubits, {len(self.gates)} gates, depth={self.depth()})"
