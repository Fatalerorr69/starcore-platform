"""Tests for STARCORE 10A Autonomous Decision Engine"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "10A"


def test_decide_best_action() -> None:
    from autonomous_decision import AutonomousDecisionEngine, DecisionContext, Action
    engine = AutonomousDecisionEngine()
    ctx = DecisionContext(
        state={"load": 0.8},
        available_actions=[
            Action("scale_out", expected_reward=10.0, cost=2.0, probability=0.9),
            Action("do_nothing", expected_reward=0.0, cost=0.0, probability=1.0),
        ]
    )
    chosen = engine.decide(ctx)
    assert chosen is not None
    assert chosen.name == "scale_out"


def test_constraint_filtering() -> None:
    from autonomous_decision import AutonomousDecisionEngine, DecisionContext, Action
    engine = AutonomousDecisionEngine()
    ctx = DecisionContext(
        state={},
        available_actions=[Action("expensive", 100.0, cost=50.0)],
        constraints={"max_cost": 10.0},
    )
    result = engine.decide(ctx)
    assert result is None
