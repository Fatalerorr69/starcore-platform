"""Tests for 18E Predictive Reality Engine"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "18E"


def test_observe_records_state():
    from reality_engine import PredictiveRealityEngine, RealityState
    engine = PredictiveRealityEngine()
    engine.observe(RealityState(1.0, {"x": 10.0}))
    assert engine._history[0].variables["x"] == 10.0


def test_predict_requires_two_states():
    from reality_engine import PredictiveRealityEngine, RealityState
    engine = PredictiveRealityEngine()
    engine.observe(RealityState(1.0, {"x": 1.0}))
    assert engine.predict() == []


def test_predict_extrapolates():
    from reality_engine import PredictiveRealityEngine, RealityState
    engine = PredictiveRealityEngine()
    engine.observe(RealityState(1.0, {"x": 1.0}))
    engine.observe(RealityState(2.0, {"x": 3.0}))
    events = engine.predict(steps=2)
    assert len(events) == 2
    # x should be increasing (delta=2 per step)
    assert events[0].state.variables["x"] > 3.0


def test_divergence_returns_float():
    from reality_engine import PredictiveRealityEngine, RealityState
    engine = PredictiveRealityEngine()
    engine.observe(RealityState(1.0, {"x": 1.0}))
    engine.observe(RealityState(2.0, {"x": 3.0}))
    engine.predict(steps=1)
    actual = RealityState(3.0, {"x": 6.5})
    d = engine.divergence(actual)
    assert isinstance(d, float)
    assert d >= 0.0
