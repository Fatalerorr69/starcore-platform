"""Tests for 16A Distributed Consciousness Mesh"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "16A"


def test_node_activation() -> None:
    from consciousness_mesh import ConsciousnessMesh, ThoughtNode
    mesh = ConsciousnessMesh()
    mesh.add_node(ThoughtNode("n1", "curiosity"))
    mesh.activate("n1", 0.8)
    assert mesh._nodes["n1"].activation == 0.8


def test_propagation_through_stream() -> None:
    from consciousness_mesh import ConsciousnessMesh, ThoughtNode, ConsciousnessStream
    mesh = ConsciousnessMesh(decay_rate=0.0)
    mesh.add_node(ThoughtNode("a", "source"))
    mesh.add_node(ThoughtNode("b", "target"))
    mesh.add_stream(ConsciousnessStream("s1", "a", "b", bandwidth=1.0))
    mesh.activate("a", 1.0)
    state = mesh.step()
    assert state["b"] > 0.0


def test_decay() -> None:
    from consciousness_mesh import ConsciousnessMesh, ThoughtNode
    mesh = ConsciousnessMesh(decay_rate=0.1)
    mesh.add_node(ThoughtNode("n1", "test"))
    mesh.activate("n1", 1.0)
    mesh.step()
    assert mesh._nodes["n1"].activation < 1.0


def test_most_active() -> None:
    from consciousness_mesh import ConsciousnessMesh, ThoughtNode
    mesh = ConsciousnessMesh(decay_rate=0.0)
    for i, act in [("a", 0.9), ("b", 0.3), ("c", 0.6)]:
        n = ThoughtNode(i, f"concept_{i}")
        mesh.add_node(n)
        mesh.activate(i, act)
    top = mesh.most_active(2)
    assert top[0][0] == "a"
    assert top[1][0] == "c"


def test_mesh_health() -> None:
    from consciousness_mesh import ConsciousnessMesh, ThoughtNode
    mesh = ConsciousnessMesh()
    mesh.add_node(ThoughtNode("x", "x"))
    mesh.add_node(ThoughtNode("y", "y"))
    health = mesh.mesh_health()
    assert health["nodes"] == 2
