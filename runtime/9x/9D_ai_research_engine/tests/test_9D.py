"""Tests for 9D AI Research Engine"""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "9D"


def test_hypothesis_cycle() -> None:
    from research_engine import ResearchEngine
    engine = ResearchEngine()
    h = engine.propose("Autonomous agents improve throughput")
    assert h.confidence == 0.5
    h.update("benchmark_result", True)
    assert h.confidence > 0.5


def test_experiment() -> None:
    from research_engine import ResearchEngine, ExperimentStatus
    engine = ResearchEngine()
    h = engine.propose("test hypothesis")
    exp = engine.design_experiment(h, "A/B test")
    result = engine.run_experiment(exp.experiment_id, {"success": True, "metric": 42})
    assert result.status == ExperimentStatus.COMPLETED
