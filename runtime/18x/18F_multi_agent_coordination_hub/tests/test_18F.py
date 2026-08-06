"""Tests for 18F Multi-Agent Coordination Hub"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "18F"


def test_task_allocation():
    from agent_coordination import CoordinationHub, CoordinationAgent, CoordinationTask, AgentRole
    hub = CoordinationHub()
    hub.register_agent(CoordinationAgent("w1", role=AgentRole.WORKER, capacity=2.0))
    hub.submit_task(CoordinationTask("t1", "task one", required_capacity=1.0))
    assignments = hub.allocate()
    assert "t1" in assignments
    assert assignments["t1"] == "w1"


def test_capacity_respected():
    from agent_coordination import CoordinationHub, CoordinationAgent, CoordinationTask, AgentRole
    hub = CoordinationHub()
    hub.register_agent(CoordinationAgent("w1", role=AgentRole.WORKER, capacity=0.5))
    hub.submit_task(CoordinationTask("t1", "heavy", required_capacity=1.0))
    assignments = hub.allocate()
    assert "t1" not in assignments


def test_agent_load_tracking():
    from agent_coordination import CoordinationAgent, CoordinationTask
    agent = CoordinationAgent("a1", capacity=2.0)
    task = CoordinationTask("t1", "work", required_capacity=1.0)
    agent.assign_task(task)
    assert agent.load == 1.0


def test_hub_stats():
    from agent_coordination import CoordinationHub, CoordinationAgent, AgentRole
    hub = CoordinationHub()
    hub.register_agent(CoordinationAgent("a1", role=AgentRole.WORKER))
    hub.register_agent(CoordinationAgent("a2", role=AgentRole.OBSERVER))
    stats = hub.hub_stats()
    assert stats["agents"] == 2
    assert stats["rounds"] == 0
