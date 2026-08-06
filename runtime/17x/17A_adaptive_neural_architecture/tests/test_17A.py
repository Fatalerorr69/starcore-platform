"""Tests for 17A Adaptive Neural Architecture"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17A"


def test_forward_pass_output_size():
    from adaptive_neural import AdaptiveNeuralNetwork, NeuralLayer, ActivationType
    net = AdaptiveNeuralNetwork()
    net.add_layer(NeuralLayer("l1", 4, 8))
    net.add_layer(NeuralLayer("l2", 8, 3))
    out = net.forward([0.1, 0.2, 0.3, 0.4])
    assert len(out) == 3


def test_relu_nonnegative():
    from adaptive_neural import AdaptiveNeuralNetwork, NeuralLayer, ActivationType
    net = AdaptiveNeuralNetwork()
    net.add_layer(NeuralLayer("l1", 2, 4, ActivationType.RELU))
    out = net.forward([-5.0, -5.0])
    assert all(v >= 0.0 for v in out)


def test_performance_recording():
    from adaptive_neural import AdaptiveNeuralNetwork
    net = AdaptiveNeuralNetwork()
    for s in [0.9, 0.85, 0.8, 0.75, 0.7]:
        net.record_performance(s)
    summary = net.architecture_summary()
    assert summary["avg_performance"] > 0.0


def test_adapt_on_decline():
    from adaptive_neural import AdaptiveNeuralNetwork, NeuralLayer
    net = AdaptiveNeuralNetwork()
    net.add_layer(NeuralLayer("l1", 2, 2))
    for s in [0.9, 0.8, 0.7, 0.6, 0.5]:
        net.record_performance(s)
    result = net.adapt()
    assert result == "pruned"
    assert net.architecture_summary()["adaptations"] == 1
