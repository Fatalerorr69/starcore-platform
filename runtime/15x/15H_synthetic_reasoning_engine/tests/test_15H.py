"""Tests for 15H Synthetic Reasoning Engine"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "15H"


def test_causal_path() -> None:
    from synthetic_reasoning import CausalGraph, CausalNode, CausalEdge
    g = CausalGraph()
    for name in ["A", "B", "C"]:
        g.add_node(CausalNode(name))
    g.add_edge(CausalEdge("A", "B"))
    g.add_edge(CausalEdge("B", "C"))
    path = g.causal_path("A", "C")
    assert path == ["A", "B", "C"]


def test_no_path() -> None:
    from synthetic_reasoning import CausalGraph, CausalNode
    g = CausalGraph()
    g.add_node(CausalNode("X"))
    g.add_node(CausalNode("Y"))
    assert g.causal_path("X", "Y") is None


def test_causes_and_effects() -> None:
    from synthetic_reasoning import CausalGraph, CausalNode, CausalEdge
    g = CausalGraph()
    for n in ["rain", "wet_ground", "slippery"]:
        g.add_node(CausalNode(n))
    g.add_edge(CausalEdge("rain", "wet_ground"))
    g.add_edge(CausalEdge("wet_ground", "slippery"))
    assert "wet_ground" in g.effects_of("rain")
    assert "rain" in g.causes_of("wet_ground")


def test_counterfactual() -> None:
    from synthetic_reasoning import CausalGraph, CausalNode, CausalEdge
    g = CausalGraph()
    g.add_node(CausalNode("effort", value=5.0))
    g.add_node(CausalNode("output", value=10.0))
    g.add_edge(CausalEdge("effort", "output", strength=2.0))
    cf = g.counterfactual({"effort": 10.0}, ["output"])
    assert "output" in cf.counterfactual_outcome
