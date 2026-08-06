"""Tests for 17E Recursive Self-Improvement"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17E"


def test_evaluation_records():
    from self_improvement import SelfImprovingAgent
    agent = SelfImprovingAgent()
    for s in [0.4, 0.5, 0.6]:
        agent.evaluate(s)
    assert agent.improvement_summary()["evaluations"] == 3


def test_propose_on_decline():
    from self_improvement import SelfImprovingAgent
    agent = SelfImprovingAgent()
    for s in [0.8, 0.6, 0.4]:
        agent.evaluate(s)
    proposals = agent.propose_improvements()
    assert len(proposals) > 0


def test_apply_changes_params():
    from self_improvement import SelfImprovingAgent
    agent = SelfImprovingAgent()
    for s in [0.8, 0.6, 0.4]:
        agent.evaluate(s)
    proposals = agent.propose_improvements()
    before_lr = agent._params["learning_rate"]
    agent.apply_improvement(proposals[0])
    assert agent._params["learning_rate"] < before_lr


def test_improvement_summary():
    from self_improvement import SelfImprovingAgent
    agent = SelfImprovingAgent()
    for s in [0.8, 0.6, 0.4]:
        agent.evaluate(s)
    for p in agent.propose_improvements():
        agent.apply_improvement(p)
    summary = agent.improvement_summary()
    assert summary["improvements_applied"] > 0
    assert summary["total_gain"] > 0.0
