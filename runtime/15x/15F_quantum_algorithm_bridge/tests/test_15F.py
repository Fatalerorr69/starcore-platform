"""Tests for 15F Quantum Algorithm Bridge"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "15F"


def test_qubit_normalization() -> None:
    from quantum_bridge import Qubit
    q = Qubit(alpha=complex(3, 0), beta=complex(4, 0))
    probs = q.probability()
    assert abs(probs["p0"] + probs["p1"] - 1.0) < 1e-9


def test_hadamard_superposition() -> None:
    from quantum_bridge import Qubit
    q = Qubit(alpha=complex(1, 0), beta=complex(0, 0))  # |0⟩
    h_q = q.apply_hadamard()
    probs = h_q.probability()
    assert abs(probs["p0"] - 0.5) < 1e-9
    assert abs(probs["p1"] - 0.5) < 1e-9


def test_pauli_x_flips() -> None:
    from quantum_bridge import Qubit
    q = Qubit(alpha=complex(1, 0), beta=complex(0, 0))  # |0⟩
    flipped = q.apply_pauli_x()
    probs = flipped.probability()
    assert probs["p0"] < 1e-9
    assert abs(probs["p1"] - 1.0) < 1e-9


def test_grover_finds_target() -> None:
    from quantum_bridge import GroverSearch
    grover = GroverSearch(n_qubits=4)
    target = 11
    found, confidence = grover.search(lambda x: x == target)
    assert found == target
    assert confidence > 0.5


def test_quantum_circuit_builder() -> None:
    from quantum_bridge import QuantumCircuit
    circuit = QuantumCircuit(3)
    circuit.h(0).cx(0, 1).cx(1, 2)
    assert circuit.depth() == 3
    assert "3 qubits" in circuit.description()
