"""Tests for 17H Causal Intervention Engine"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17H"


def test_intervention_propagates():
    from causal_intervention import CausalInterventionEngine, CausalVariable, CausalEdge
    eng = CausalInterventionEngine()
    eng.add_variable(CausalVariable("rain", "Rain"))
    eng.add_variable(CausalVariable("wet", "Wet ground"))
    eng.add_edge(CausalEdge("rain", "wet", strength=1.0))
    result = eng.intervene("rain", 1.0)
    assert result.effects.get("wet") == 1.0


def test_chain_propagation():
    from causal_intervention import CausalInterventionEngine, CausalVariable, CausalEdge
    eng = CausalInterventionEngine()
    for vid in ["a", "b", "c"]:
        eng.add_variable(CausalVariable(vid, vid))
    eng.add_edge(CausalEdge("a", "b", 0.5))
    eng.add_edge(CausalEdge("b", "c", 0.5))
    result = eng.intervene("a", 1.0)
    assert abs(result.effects["b"] - 0.5) < 1e-9
    assert abs(result.effects["c"] - 0.25) < 1e-9


def test_causal_path():
    from causal_intervention import CausalInterventionEngine, CausalVariable, CausalEdge
    eng = CausalInterventionEngine()
    for vid in ["x", "y", "z"]:
        eng.add_variable(CausalVariable(vid, vid))
    eng.add_edge(CausalEdge("x", "y"))
    eng.add_edge(CausalEdge("y", "z"))
    assert eng.causal_path("x", "z") == ["x", "y", "z"]


def test_no_causal_path():
    from causal_intervention import CausalInterventionEngine, CausalVariable
    eng = CausalInterventionEngine()
    eng.add_variable(CausalVariable("p", "P"))
    eng.add_variable(CausalVariable("q", "Q"))
    assert eng.causal_path("p", "q") == []


def test_counterfactual():
    from causal_intervention import CausalInterventionEngine, CausalVariable, CausalEdge
    eng = CausalInterventionEngine()
    eng.add_variable(CausalVariable("cause", "Cause", value=0.0))
    eng.add_variable(CausalVariable("effect", "Effect", value=0.0))
    eng.add_edge(CausalEdge("cause", "effect", strength=2.0))
    factual, cf = eng.counterfactual("cause", 3.0, "effect")
    assert cf == 6.0
