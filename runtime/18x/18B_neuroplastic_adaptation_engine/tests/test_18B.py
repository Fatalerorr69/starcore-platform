"""Tests for 18B Neuroplastic Adaptation Engine"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "18B"


def test_connection_strengthening():
    from neuroplastic import SynapticConnection
    conn = SynapticConnection("a", "b", weight=0.5)
    conn.strengthen(1.0)
    assert conn.weight > 0.5


def test_connection_weakening():
    from neuroplastic import SynapticConnection
    conn = SynapticConnection("a", "b", weight=0.5)
    conn.weaken(1.0)
    assert conn.weight < 0.5


def test_layer_activation():
    from neuroplastic import NeuroplasticLayer
    layer = NeuroplasticLayer("L1", neurons=3)
    out = layer.activate([1.0, -1.0, 0.5])
    assert len(out) == 3
    assert all(-1.0 <= v <= 1.0 for v in out)


def test_pruning_removes_weak():
    from neuroplastic import NeuroplasticLayer, SynapticConnection
    layer = NeuroplasticLayer("L2")
    layer.add_connection(SynapticConnection("a", "b", weight=0.05))
    layer.add_connection(SynapticConnection("c", "d", weight=0.8))
    removed = layer.prune(threshold=0.1)
    assert removed == 1
    assert len(layer.connections) == 1
