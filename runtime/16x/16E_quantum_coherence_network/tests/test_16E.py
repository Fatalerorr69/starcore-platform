"""Tests for 16E Quantum Coherence Network"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "16E"


def test_bell_state_normalization() -> None:
    from quantum_coherence import QuantumCoherenceNetwork
    net = QuantumCoherenceNetwork()
    state = net.create_bell_state("phi_plus")
    norm = state.norm()
    assert abs(norm - 1.0) < 1e-9


def test_entanglement_creation() -> None:
    from quantum_coherence import QuantumCoherenceNetwork
    net = QuantumCoherenceNetwork()
    pair = net.entangle("p1", 0, 1)
    assert pair.fidelity == 1.0
    assert net.network_health()["pairs"] == 1


def test_decoherence_reduces_fidelity() -> None:
    from quantum_coherence import QuantumCoherenceNetwork
    net = QuantumCoherenceNetwork()
    net.entangle("p1", 0, 1)
    for _ in range(10):
        net.tick_decoherence()
    assert net._pairs["p1"].fidelity < 1.0


def test_teleport_with_high_fidelity() -> None:
    from quantum_coherence import QuantumCoherenceNetwork
    net = QuantumCoherenceNetwork()
    net.entangle("p1", 0, 1)
    result = net.teleport("p1", 42.0)
    assert result is not None
    assert abs(result - 42.0) < 1.0


def test_teleport_fails_low_fidelity() -> None:
    from quantum_coherence import QuantumCoherenceNetwork
    net = QuantumCoherenceNetwork()
    pair = net.entangle("p1", 0, 1)
    pair.fidelity = 0.1
    result = net.teleport("p1", 42.0)
    assert result is None
