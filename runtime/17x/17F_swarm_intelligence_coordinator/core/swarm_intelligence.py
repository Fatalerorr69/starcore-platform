"""17F — Swarm Intelligence Coordinator: pheromone-based stigmergic swarm."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import random
import time


class AgentState(str, Enum):
    SEARCHING = "searching"
    EXPLOITING = "exploiting"
    RETURNING = "returning"


@dataclass
class SwarmAgent:
    agent_id: str
    x: float = 0.0
    y: float = 0.0
    state: AgentState = AgentState.SEARCHING
    carried_resource: float = 0.0
    steps: int = 0


@dataclass
class PheromoneCell:
    x: int
    y: int
    strength: float = 0.0

    def evaporate(self, rate: float = 0.05) -> None:
        self.strength = max(0.0, self.strength * (1.0 - rate))


class StigmergicSwarm:
    def __init__(self, grid_size: int = 20, evaporation_rate: float = 0.05) -> None:
        self._grid = grid_size
        self._evap = evaporation_rate
        self._pheromones: dict[tuple[int, int], PheromoneCell] = {}
        self._agents: dict[str, SwarmAgent] = {}
        self._resources: dict[tuple[int, int], float] = {}
        self._collected: float = 0.0
        self._ticks = 0

    def add_agent(self, agent: SwarmAgent) -> None:
        self._agents[agent.agent_id] = agent

    def place_resource(self, x: int, y: int, amount: float) -> None:
        self._resources[(x, y)] = amount

    def deposit_pheromone(self, x: int, y: int, strength: float) -> None:
        key = (x, y)
        if key not in self._pheromones:
            self._pheromones[key] = PheromoneCell(x, y)
        self._pheromones[key].strength = min(1.0, self._pheromones[key].strength + strength)

    def _pheromone_at(self, x: int, y: int) -> float:
        return self._pheromones.get((x, y), PheromoneCell(x, y)).strength

    def _move(self, agent: SwarmAgent) -> None:
        # Collect resource at current position before moving
        cur = (int(agent.x), int(agent.y))
        if cur in self._resources and self._resources[cur] > 0:
            take = min(1.0, self._resources[cur])
            agent.carried_resource += take
            self._resources[cur] -= take
            agent.state = AgentState.EXPLOITING
            self.deposit_pheromone(cur[0], cur[1], 0.5)
        neighbors = [
            (max(0, int(agent.x) - 1), int(agent.y)),
            (min(self._grid - 1, int(agent.x) + 1), int(agent.y)),
            (int(agent.x), max(0, int(agent.y) - 1)),
            (int(agent.x), min(self._grid - 1, int(agent.y) + 1)),
        ]
        weights = [self._pheromone_at(nx, ny) + 0.1 for nx, ny in neighbors]
        total = sum(weights)
        r = random.random() * total
        cumulative = 0.0
        chosen = neighbors[0]
        for (nx, ny), w in zip(neighbors, weights):
            cumulative += w
            if r <= cumulative:
                chosen = (nx, ny)
                break
        agent.x, agent.y = float(chosen[0]), float(chosen[1])
        agent.steps += 1
        pos = (int(agent.x), int(agent.y))
        if pos in self._resources and self._resources[pos] > 0:
            take = min(1.0, self._resources[pos])
            agent.carried_resource += take
            self._resources[pos] -= take
            agent.state = AgentState.EXPLOITING
            self.deposit_pheromone(pos[0], pos[1], 0.5)

    def tick(self) -> dict[str, Any]:
        self._ticks += 1
        for agent in self._agents.values():
            self._move(agent)
            if agent.carried_resource > 0 and int(agent.x) == 0 and int(agent.y) == 0:
                self._collected += agent.carried_resource
                agent.carried_resource = 0.0
                agent.state = AgentState.SEARCHING
        for cell in self._pheromones.values():
            cell.evaporate(self._evap)
        return {"ticks": self._ticks, "collected": self._collected}

    def swarm_stats(self) -> dict[str, Any]:
        return {"agents": len(self._agents), "ticks": self._ticks,
                "total_collected": round(self._collected, 4),
                "pheromone_cells": len(self._pheromones)}
