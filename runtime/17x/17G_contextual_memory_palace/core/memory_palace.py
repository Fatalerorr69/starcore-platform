"""17G — Contextual Memory Palace: method-of-loci spatial memory system."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import time


@dataclass
class MemoryAnchor:
    anchor_id: str
    location: str  # "room_id/spot"
    content: Any
    tags: list[str] = field(default_factory=list)
    strength: float = 1.0
    access_count: int = 0
    created_at: float = field(default_factory=time.time)

    def recall(self) -> Any:
        self.access_count += 1
        return self.content

    def reinforce(self, amount: float = 0.1) -> None:
        self.strength = min(1.0, self.strength + amount)

    def decay(self, rate: float = 0.01) -> None:
        self.strength = max(0.0, self.strength - rate / (1.0 + self.access_count))


@dataclass
class Room:
    room_id: str
    name: str
    description: str = ""
    capacity: int = 20
    anchors: list[str] = field(default_factory=list)


class MemoryPalace:
    def __init__(self) -> None:
        self._rooms: dict[str, Room] = {}
        self._anchors: dict[str, MemoryAnchor] = {}
        self._location_index: dict[str, list[str]] = {}

    def add_room(self, room: Room) -> None:
        self._rooms[room.room_id] = room

    def store(self, anchor: MemoryAnchor) -> bool:
        room_id = anchor.location.split("/")[0]
        room = self._rooms.get(room_id)
        if room and len(room.anchors) >= room.capacity:
            return False
        self._anchors[anchor.anchor_id] = anchor
        if room:
            room.anchors.append(anchor.anchor_id)
        self._location_index.setdefault(anchor.location, []).append(anchor.anchor_id)
        return True

    def recall_by_location(self, location: str) -> list[Any]:
        return [self._anchors[aid].recall()
                for aid in self._location_index.get(location, [])
                if aid in self._anchors]

    def recall_by_tag(self, tag: str) -> list[MemoryAnchor]:
        return [a for a in self._anchors.values() if tag in a.tags]

    def walk(self, room_id: str) -> list[MemoryAnchor]:
        room = self._rooms.get(room_id)
        if not room:
            return []
        return [self._anchors[aid] for aid in room.anchors if aid in self._anchors]

    def decay_all(self, rate: float = 0.01) -> None:
        for anchor in self._anchors.values():
            anchor.decay(rate)

    def palace_stats(self) -> dict[str, Any]:
        return {
            "rooms": len(self._rooms),
            "anchors": len(self._anchors),
            "avg_strength": round(
                sum(a.strength for a in self._anchors.values()) / max(1, len(self._anchors)), 4),
        }
