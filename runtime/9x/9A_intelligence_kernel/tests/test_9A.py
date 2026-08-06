"""Tests for 9A Intelligence Kernel"""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    p = Path(__file__).parent.parent / "registry" / "manifest.json"
    data = json.loads(p.read_text())
    assert data["layer"] == "9A"
    assert data["status"] == "PRODUCTION"


def test_health() -> None:
    p = Path(__file__).parent.parent / "runtime" / "health.json"
    data = json.loads(p.read_text())
    assert data["status"] == "healthy"
    assert data["errors"] == 0


def test_reasoning_engine() -> None:
    from reasoning_engine import ReasoningEngine, Belief, ReasoningMode
    engine = ReasoningEngine()
    engine.add_belief(Belief("sky is blue", 0.99, ["observation"], ReasoningMode.INDUCTIVE))
    results = engine.infer("sky")
    assert len(results) == 1
    assert results[0].confidence == 0.99


def test_goal_planner() -> None:
    from goal_planner import GoalPlanner, PlanStep
    planner = GoalPlanner()
    planner.register_action(PlanStep("deploy", [], ["deployed"], 1.0))
    planner.set_world_state(set())
    steps = planner.plan_to_goal("deployed")
    assert len(steps) == 1
    assert steps[0].action == "deploy"
