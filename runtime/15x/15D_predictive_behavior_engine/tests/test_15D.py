"""Tests for 15D Predictive Behavior Engine"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "15D"


def test_prediction_after_observations() -> None:
    from predictive_engine import TimeSeriesPredictor, Observation
    predictor = TimeSeriesPredictor()
    for i in range(20):
        predictor.observe(Observation(value=float(i) * 2.0))
    pred = predictor.predict(horizon_steps=3)
    assert pred.confidence > 0.0
    assert pred.predicted_value > 30.0  # trend should continue upward


def test_anomaly_detection() -> None:
    from predictive_engine import TimeSeriesPredictor, Observation
    predictor = TimeSeriesPredictor()
    for _ in range(30):
        predictor.observe(Observation(value=100.0))
    assert not predictor.is_anomaly(101.0)
    assert predictor.is_anomaly(200.0)


def test_scenario_simulation() -> None:
    from predictive_engine import TimeSeriesPredictor, ScenarioSimulator, Observation
    predictor = TimeSeriesPredictor()
    for i in range(15):
        predictor.observe(Observation(float(i)))
    sim = ScenarioSimulator(predictor)
    scenarios = sim.simulate(horizon_steps=5)
    assert len(scenarios) == 3
    names = {s.name for s in scenarios}
    assert "optimistic" in names and "pessimistic" in names and "baseline" in names
    total_prob = sum(s.probability for s in scenarios)
    assert abs(total_prob - 1.0) < 0.01
