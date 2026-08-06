"""Tests for 18C Emergent Consciousness Framework"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "18C"


def test_property_emergence():
    from emergence import EmergentProperty
    prop = EmergentProperty("awareness")
    result = prop.emerge(0.5)
    assert result > 0.0
    assert prop.interactions == 1


def test_consciousness_dormant_initially():
    from emergence import EmergenceEngine, ConsciousnessLevel
    engine = EmergenceEngine()
    assert engine.consciousness_level == ConsciousnessLevel.DORMANT


def test_consciousness_rises_with_stimulation():
    from emergence import EmergenceEngine
    engine = EmergenceEngine()
    for _ in range(20):
        engine.stimulate({"awareness": 1.0, "attention": 1.0, "memory": 1.0})
    assert engine._integration > 0.0
    assert engine.consciousness_level.value != "dormant"


def test_report_keys():
    from emergence import EmergenceEngine
    engine = EmergenceEngine()
    engine.stimulate({"a": 0.5})
    report = engine.report()
    for key in ("properties", "integration", "level", "steps"):
        assert key in report
