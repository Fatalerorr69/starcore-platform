"""Tests for 15G Neuromorphic Computing Interface"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "15G"


def test_neuron_fires_above_threshold() -> None:
    from neuromorphic import Neuron
    n = Neuron("n1", threshold=0.05)
    fired = False
    for _ in range(200):
        if n.receive(5.0, dt=0.001):
            fired = True
            break
    assert fired
    assert n.spike_count >= 1


def test_hebbian_weight_strengthening() -> None:
    from neuromorphic import SpikingNetwork, Neuron, Synapse
    net = SpikingNetwork(learning_rate=0.05)
    net.add_neuron(Neuron("pre", threshold=0.1))
    net.add_neuron(Neuron("post", threshold=0.1))
    syn = Synapse("pre", "post", weight=0.3)
    net.connect(syn)
    initial_weight = syn.weight
    for _ in range(50):
        net.step({"pre": 5.0, "post": 5.0})
    assert syn.weight >= initial_weight  # Hebbian: should not decrease on co-firing


def test_network_stats() -> None:
    from neuromorphic import SpikingNetwork, Neuron
    net = SpikingNetwork()
    net.add_neuron(Neuron("a"))
    net.add_neuron(Neuron("b"))
    stats = net.network_stats()
    assert stats["neurons"] == 2
    assert stats["synapses"] == 0
