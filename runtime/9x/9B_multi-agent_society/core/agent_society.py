"""9B — Multi-Agent Society: Agent Society"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol
import uuid


class AgentRole(str, Enum):
    RESEARCHER = "researcher"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"


@dataclass
class Agent:
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    role: AgentRole = AgentRole.EXECUTOR
    capabilities: list[str] = field(default_factory=list)
    coalition_id: str | None = None
    status: str = "idle"


@dataclass
class Coalition:
    coalition_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    goal: str = ""
    members: list[str] = field(default_factory=list)
    active: bool = True


class AgentSociety:
    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}
        self._coalitions: dict[str, Coalition] = {}

    def spawn(self, role: AgentRole, capabilities: list[str]) -> Agent:
        agent = Agent(role=role, capabilities=capabilities)
        self._agents[agent.agent_id] = agent
        return agent

    def form_coalition(self, goal: str, agent_ids: list[str]) -> Coalition:
        coalition = Coalition(goal=goal, members=agent_ids)
        self._coalitions[coalition.coalition_id] = coalition
        for aid in agent_ids:
            if aid in self._agents:
                self._agents[aid].coalition_id = coalition.coalition_id
        return coalition

    def resolve_conflict(self, agent_a: str, agent_b: str, resource: str) -> str:
        a = self._agents.get(agent_a)
        b = self._agents.get(agent_b)
        if not a or not b:
            return "unknown"
        priority = {AgentRole.COORDINATOR: 4, AgentRole.SPECIALIST: 3,
                    AgentRole.RESEARCHER: 2, AgentRole.REVIEWER: 1, AgentRole.EXECUTOR: 0}
        winner = agent_a if priority.get(a.role, 0) >= priority.get(b.role, 0) else agent_b
        return winner

    def society_health(self) -> dict[str, Any]:
        return {
            "agents": len(self._agents),
            "coalitions": len(self._coalitions),
            "idle": sum(1 for a in self._agents.values() if a.status == "idle"),
            "status": "ok",
        }
