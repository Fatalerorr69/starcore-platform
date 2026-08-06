"""Tests for 16B Temporal Intelligence Engine"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "16B"


def test_record_events() -> None:
    from temporal_engine import TemporalIntelligence, TemporalEvent
    ti = TemporalIntelligence()
    for i in range(5):
        ti.record_event(TemporalEvent(f"e{i}", float(i), tags=["ping"]))
    assert ti.event_count() == 5


def test_detect_periodicity() -> None:
    from temporal_engine import TemporalIntelligence, TemporalEvent
    ti = TemporalIntelligence()
    for i in range(6):
        ti.record_event(TemporalEvent(f"e{i}", float(i) * 10.0, tags=["heartbeat"]))
    pattern = ti.detect_periodicity("heartbeat")
    assert pattern is not None
    assert abs(pattern.period_seconds - 10.0) < 0.01
    assert pattern.confidence > 0.9


def test_next_expected() -> None:
    from temporal_engine import TemporalIntelligence, TemporalEvent
    ti = TemporalIntelligence()
    for i in range(5):
        ti.record_event(TemporalEvent(f"e{i}", float(i) * 5.0, tags=["tick"]))
    pattern = ti.detect_periodicity("tick")
    assert pattern is not None
    nxt = ti.next_expected(pattern.pattern_id)
    assert nxt is not None
    assert nxt > pattern.last_seen
