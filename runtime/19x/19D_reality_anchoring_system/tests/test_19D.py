"""Tests for 19D Reality Anchoring System"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "19D"


def test_anchor_valid_observation():
    from reality_anchor import AnchorPoint
    anchor = AnchorPoint("a1", "speed", value=100.0, tolerance=5.0)
    assert anchor.is_valid(102.0)
    assert not anchor.is_valid(110.0)


def test_drift_detected():
    from reality_anchor import RealityAnchoringSystem, AnchorPoint
    system = RealityAnchoringSystem()
    system.register_anchor(AnchorPoint("a1", "temp", value=20.0, tolerance=1.0))
    drifts = system.check({"a1": 25.0})
    assert len(drifts) == 1
    assert drifts[0].anchor_id == "a1"


def test_no_drift_within_tolerance():
    from reality_anchor import RealityAnchoringSystem, AnchorPoint
    system = RealityAnchoringSystem()
    system.register_anchor(AnchorPoint("a1", "temp", value=20.0, tolerance=5.0))
    drifts = system.check({"a1": 22.0})
    assert len(drifts) == 0


def test_system_stats():
    from reality_anchor import RealityAnchoringSystem, AnchorPoint
    system = RealityAnchoringSystem()
    system.register_anchor(AnchorPoint("a1", "x", value=0.0))
    system.check({"a1": 0.0})
    stats = system.system_stats()
    assert stats["anchors"] == 1
    assert stats["checks"] == 1
