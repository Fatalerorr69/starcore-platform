"""Tests for 16D Reality Simulation Engine"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "16D"


def test_entity_movement() -> None:
    from reality_simulator import RealitySimulator, SimEntity, EntityType, Vector2D
    sim = RealitySimulator()
    e = SimEntity("a1", EntityType.AGENT, position=Vector2D(100.0, 100.0),
                  velocity=Vector2D(10.0, 0.0))
    sim.add_entity(e)
    sim.step(dt=1.0)
    assert e.position.x > 100.0


def test_boundary_collision() -> None:
    from reality_simulator import RealitySimulator, SimEntity, EntityType, Vector2D
    sim = RealitySimulator(width=100.0, height=100.0)
    e = SimEntity("b1", EntityType.OBJECT, position=Vector2D(95.0, 50.0),
                  velocity=Vector2D(100.0, 0.0))
    sim.add_entity(e)
    result = sim.step(dt=1.0)
    assert result["boundary_collisions"] >= 1
    assert e.position.x <= 100.0


def test_nearest_entities() -> None:
    from reality_simulator import RealitySimulator, SimEntity, EntityType, Vector2D
    sim = RealitySimulator()
    sim.add_entity(SimEntity("c1", EntityType.AGENT, position=Vector2D(0.0, 0.0)))
    sim.add_entity(SimEntity("c2", EntityType.OBJECT, position=Vector2D(5.0, 0.0)))
    sim.add_entity(SimEntity("c3", EntityType.OBJECT, position=Vector2D(500.0, 0.0)))
    near = sim.nearest_entities("c1", radius=10.0)
    assert "c2" in near
    assert "c3" not in near


def test_simulation_state() -> None:
    from reality_simulator import RealitySimulator, SimEntity, EntityType, Vector2D
    sim = RealitySimulator()
    sim.add_entity(SimEntity("d1", EntityType.RESOURCE, position=Vector2D(10.0, 10.0)))
    state = sim.simulation_state()
    assert state["entities"] == 1
    assert state["tick"] == 0
