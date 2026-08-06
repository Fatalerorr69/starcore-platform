"""Tests for 17G Contextual Memory Palace"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17G"


def test_store_and_recall_by_location():
    from memory_palace import MemoryPalace, Room, MemoryAnchor
    palace = MemoryPalace()
    palace.add_room(Room("hall", "Great Hall"))
    palace.store(MemoryAnchor("a1", "hall/fireplace", "warmth of home"))
    recalled = palace.recall_by_location("hall/fireplace")
    assert recalled == ["warmth of home"]


def test_recall_by_tag():
    from memory_palace import MemoryPalace, Room, MemoryAnchor
    palace = MemoryPalace()
    palace.add_room(Room("lab", "Laboratory"))
    palace.store(MemoryAnchor("a1", "lab/bench", "quantum formula", tags=["science"]))
    palace.store(MemoryAnchor("a2", "lab/shelf", "recipe", tags=["cooking"]))
    results = palace.recall_by_tag("science")
    assert len(results) == 1
    assert results[0].anchor_id == "a1"


def test_room_walk():
    from memory_palace import MemoryPalace, Room, MemoryAnchor
    palace = MemoryPalace()
    palace.add_room(Room("garden", "Garden"))
    palace.store(MemoryAnchor("a1", "garden/pond", "reflection"))
    palace.store(MemoryAnchor("a2", "garden/path", "direction"))
    anchors = palace.walk("garden")
    assert len(anchors) == 2


def test_decay_reduces_strength():
    from memory_palace import MemoryPalace, Room, MemoryAnchor
    palace = MemoryPalace()
    palace.add_room(Room("r1", "Room 1"))
    palace.store(MemoryAnchor("a1", "r1/spot", "memory"))
    before = palace._anchors["a1"].strength
    palace.decay_all(rate=0.1)
    assert palace._anchors["a1"].strength < before


def test_room_capacity_limit():
    from memory_palace import MemoryPalace, Room, MemoryAnchor
    palace = MemoryPalace()
    palace.add_room(Room("tiny", "Tiny Room", capacity=2))
    assert palace.store(MemoryAnchor("a1", "tiny/s1", "x")) is True
    assert palace.store(MemoryAnchor("a2", "tiny/s2", "y")) is True
    assert palace.store(MemoryAnchor("a3", "tiny/s3", "z")) is False
