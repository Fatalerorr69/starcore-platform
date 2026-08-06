"""Tests for 17F Swarm Intelligence Coordinator"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17F"


def test_pheromone_deposit_and_evaporate():
    from swarm_intelligence import StigmergicSwarm
    swarm = StigmergicSwarm(evaporation_rate=0.5)
    swarm.deposit_pheromone(5, 5, 0.8)
    assert swarm._pheromone_at(5, 5) == 0.8
    swarm._pheromones[(5, 5)].evaporate(0.5)
    assert swarm._pheromone_at(5, 5) < 0.8


def test_agent_moves():
    from swarm_intelligence import StigmergicSwarm, SwarmAgent
    swarm = StigmergicSwarm()
    agent = SwarmAgent("a1", x=5.0, y=5.0)
    swarm.add_agent(agent)
    swarm.tick()
    assert agent.steps == 1


def test_resource_collection():
    from swarm_intelligence import StigmergicSwarm, SwarmAgent
    swarm = StigmergicSwarm(grid_size=5)
    agent = SwarmAgent("a1", x=1.0, y=0.0)
    swarm.add_agent(agent)
    swarm.place_resource(1, 0, 5.0)
    swarm.tick()
    # Agent at (1,0) should pick up resource
    assert agent.carried_resource > 0 or swarm._resources.get((1, 0), 5.0) < 5.0


def test_swarm_stats():
    from swarm_intelligence import StigmergicSwarm, SwarmAgent
    swarm = StigmergicSwarm()
    swarm.add_agent(SwarmAgent("a1"))
    swarm.add_agent(SwarmAgent("a2"))
    swarm.tick()
    stats = swarm.swarm_stats()
    assert stats["agents"] == 2
    assert stats["ticks"] == 1
