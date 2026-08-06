"""Tests for 18A Quantum Entanglement Network"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "18A"


def test_pair_creation():
    from quantum_entanglement import QuantumEntanglementNetwork
    net = QuantumEntanglementNetwork()
    pair = net.create_pair("p1", fidelity=1.0)
    assert pair.pair_id == "p1"
    assert pair.is_entangled


def test_decoherence_reduces_fidelity():
    from quantum_entanglement import EntangledPair
    p = EntangledPair("p0", fidelity=1.0)
    p.decohere(0.3)
    assert p.fidelity < 1.0


def test_transmission_returns_dict():
    from quantum_entanglement import QuantumEntanglementNetwork
    net = QuantumEntanglementNetwork()
    net.create_pair("p2")
    result = net.transmit("p2", 1)
    assert "transmitted" in result
    assert result["transmitted"] == 1


def test_network_stats():
    from quantum_entanglement import QuantumEntanglementNetwork
    net = QuantumEntanglementNetwork()
    net.create_pair("a")
    net.create_pair("b")
    stats = net.network_stats()
    assert stats["pairs"] == 2
    assert stats["transmissions"] == 0
