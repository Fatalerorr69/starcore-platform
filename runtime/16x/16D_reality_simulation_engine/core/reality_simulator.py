"""16D — Reality Simulation Engine: Discrete-time 2D physics simulation."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import math
import time


class EntityType(str, Enum):
    AGENT = "agent"
    OBJECT = "object"
    RESOURCE = "resource"
    BOUNDARY = "boundary"


@dataclass
class Vector2D:
    x: float = 0.0
    y: float = 0.0

    def distance_to(self, other: "Vector2D") -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __add__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)


@dataclass
class SimEntity:
    entity_id: str
    entity_type: EntityType
    position: Vector2D = field(default_factory=Vector2D)
    velocity: Vector2D = field(default_factory=Vector2D)
    mass: float = 1.0
    energy: float = 100.0
    metadata: dict[str, Any] = field(default_factory=dict)


class RealitySimulator:
    def __init__(self, width: float = 1000.0, height: float = 1000.0,
                 friction: float = 0.95) -> None:
        self._width = width
        self._height = height
        self._friction = friction
        self._entities: dict[str, SimEntity] = {}
        self._tick = 0

    def add_entity(self, entity: SimEntity) -> None:
        self._entities[entity.entity_id] = entity

    def remove_entity(self, entity_id: str) -> None:
        self._entities.pop(entity_id, None)

    def apply_force(self, entity_id: str, force: Vector2D) -> None:
        e = self._entities.get(entity_id)
        if e:
            e.velocity.x += force.x / e.mass
            e.velocity.y += force.y / e.mass

    def step(self, dt: float = 0.1) -> dict[str, Any]:
        self._tick += 1
        collisions = 0
        for entity in self._entities.values():
            entity.position.x += entity.velocity.x * dt
            entity.position.y += entity.velocity.y * dt
            entity.velocity.x *= self._friction
            entity.velocity.y *= self._friction
            if entity.position.x < 0 or entity.position.x > self._width:
                entity.velocity.x *= -0.8
                entity.position.x = max(0.0, min(self._width, entity.position.x))
                collisions += 1
            if entity.position.y < 0 or entity.position.y > self._height:
                entity.velocity.y *= -0.8
                entity.position.y = max(0.0, min(self._height, entity.position.y))
                collisions += 1
        return {"tick": self._tick, "entities": len(self._entities),
                "boundary_collisions": collisions}

    def nearest_entities(self, entity_id: str, radius: float) -> list[str]:
        source = self._entities.get(entity_id)
        if not source:
            return []
        return [eid for eid, e in self._entities.items()
                if eid != entity_id and source.position.distance_to(e.position) <= radius]

    def simulation_state(self) -> dict[str, Any]:
        return {"tick": self._tick, "entities": len(self._entities),
                "width": self._width, "height": self._height}
