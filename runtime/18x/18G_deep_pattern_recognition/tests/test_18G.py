"""Tests for 18G Deep Pattern Recognition"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "18G"


def test_observe_creates_patterns():
    from pattern_recognition import DeepPatternEngine
    engine = DeepPatternEngine()
    engine.observe(1)
    engine.observe(2)
    assert len(engine._patterns) > 0


def test_repeated_pattern_reinforced():
    from pattern_recognition import DeepPatternEngine
    engine = DeepPatternEngine()
    # Feed same sequence twice
    for _ in range(2):
        engine.observe("A")
        engine.observe("B")
    # [A,B] pattern should appear at frequency > 1
    top = engine.top_patterns(1)
    assert len(top) > 0
    assert top[0].frequency >= 2


def test_top_patterns_sorted():
    from pattern_recognition import DeepPatternEngine
    engine = DeepPatternEngine()
    for _ in range(5):
        engine.observe("X")
        engine.observe("Y")
    tops = engine.top_patterns(3)
    freqs = [p.frequency for p in tops]
    assert freqs == sorted(freqs, reverse=True)


def test_engine_stats():
    from pattern_recognition import DeepPatternEngine
    engine = DeepPatternEngine()
    engine.observe(42)
    engine.observe(43)
    stats = engine.engine_stats()
    assert "patterns" in stats
    assert stats["observations"] == 2
