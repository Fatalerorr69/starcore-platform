"""Tests for 18I Unified Theory of Mind"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "18I"


def test_layer_activation_clamped():
    from unified_mind import UnifiedMind, MindLayer
    mind = UnifiedMind()
    mind.activate_layer(MindLayer.COGNITIVE, 2.0)  # should clamp to 1.0
    assert mind._states[MindLayer.COGNITIVE].activation == 1.0


def test_integration_weighted():
    from unified_mind import UnifiedMind, MindLayer, LAYER_WEIGHTS
    mind = UnifiedMind()
    mind.activate_layer(MindLayer.COGNITIVE, 1.0)
    coherence = mind.integrate()
    assert abs(coherence - LAYER_WEIGHTS[MindLayer.COGNITIVE]) < 1e-9


def test_dominant_layer():
    from unified_mind import UnifiedMind, MindLayer
    mind = UnifiedMind()
    mind.activate_layer(MindLayer.SENSORY, 0.1)
    mind.activate_layer(MindLayer.METACOGNITIVE, 0.9)
    assert mind.dominant_layer == MindLayer.METACOGNITIVE


def test_introspect_keys():
    from unified_mind import UnifiedMind
    mind = UnifiedMind()
    mind.integrate()
    report = mind.introspect()
    for key in ("coherence", "cycles", "layers"):
        assert key in report
    assert report["cycles"] == 1
