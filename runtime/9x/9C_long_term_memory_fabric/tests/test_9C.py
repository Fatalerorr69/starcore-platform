"""Tests for 9C Long Term Memory Fabric"""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "9C"


def test_store_and_recall() -> None:
    from memory_fabric import LongTermMemory, MemoryTrace, MemoryType
    mem = LongTermMemory()
    trace = MemoryTrace("STARCORE build completed", MemoryType.EPISODIC, importance=0.9)
    mem.store(trace)
    results = mem.recall("STARCORE")
    assert len(results) == 1
    assert results[0].access_count == 1


def test_memory_types() -> None:
    from memory_fabric import LongTermMemory, MemoryTrace, MemoryType
    mem = LongTermMemory()
    mem.store(MemoryTrace("episode 1", MemoryType.EPISODIC))
    mem.store(MemoryTrace("fact about AI", MemoryType.SEMANTIC))
    stats = mem.stats()
    assert stats["episodic"] == 1
    assert stats["semantic"] == 1


def test_consolidation() -> None:
    from memory_fabric import LongTermMemory, MemoryTrace, MemoryType
    mem = LongTermMemory(capacity=10)
    for i in range(15):
        mem.store(MemoryTrace(f"trace {i}", MemoryType.SEMANTIC, importance=float(i) / 15))
    assert len(mem._traces) <= 10
