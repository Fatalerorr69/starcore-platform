"""Tests for 9B Multi-Agent Society"""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "9B"


def test_agent_spawning() -> None:
    from agent_society import AgentSociety, AgentRole
    society = AgentSociety()
    agent = society.spawn(AgentRole.RESEARCHER, ["nlp", "search"])
    assert agent.role == AgentRole.RESEARCHER
    assert len(society._agents) == 1


def test_coalition() -> None:
    from agent_society import AgentSociety, AgentRole
    society = AgentSociety()
    a1 = society.spawn(AgentRole.COORDINATOR, [])
    a2 = society.spawn(AgentRole.EXECUTOR, [])
    coalition = society.form_coalition("build_system", [a1.agent_id, a2.agent_id])
    assert len(coalition.members) == 2


def test_conflict_resolution() -> None:
    from agent_society import AgentSociety, AgentRole
    society = AgentSociety()
    coord = society.spawn(AgentRole.COORDINATOR, [])
    exec_ = society.spawn(AgentRole.EXECUTOR, [])
    winner = society.resolve_conflict(coord.agent_id, exec_.agent_id, "gpu")
    assert winner == coord.agent_id
