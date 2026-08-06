"""Tests for 15B Emergent Intelligence Layer"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "15B"


def test_signal_ingestion() -> None:
    from emergent_intelligence import EmergenceDetector, Signal
    det = EmergenceDetector()
    for i in range(10):
        det.ingest(Signal("sensor-A", float(i)))
    assert len(det._window) == 10


def test_pattern_detection_correlated() -> None:
    from emergent_intelligence import EmergenceDetector, Signal
    det = EmergenceDetector(threshold=0.5)
    for i in range(20):
        v = float(i)
        det.ingest(Signal("src-X", v))
        det.ingest(Signal("src-Y", v * 1.01))  # near-perfect correlation
    patterns = det.detect()
    assert len(patterns) >= 1
    assert any("src-X" in p.pattern_id and "src-Y" in p.pattern_id for p in patterns)


def test_complexity_score_increases_with_diversity() -> None:
    from emergent_intelligence import EmergenceDetector, Signal
    det = EmergenceDetector()
    det.ingest(Signal("a", 1.0))
    s1 = det.complexity_score()
    for i in range(10):
        det.ingest(Signal(f"src-{i}", float(i * 3.7)))
    s2 = det.complexity_score()
    assert s2 > s1
