"""Tests for 16I Autonomous Civilization Layer"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "16I"


def test_institution_operation() -> None:
    from civilization_engine import Institution, InstitutionType
    inst = Institution("gov1", InstitutionType.GOVERNANCE, "World Council",
                       efficiency=1.0, trust_level=1.0, resources=100.0)
    output = inst.operate()
    assert output == 100.0
    assert inst.resources < 100.0


def test_society_development() -> None:
    from civilization_engine import CivilizationEngine, Society, Institution, InstitutionType
    engine = CivilizationEngine()
    engine.add_society(Society("s1", "Alpha", population=1000, cooperation_index=1.0))
    engine.add_institution(Institution("edu1", InstitutionType.EDUCATION, "Academy"))
    before_stab = engine._societies["s1"].stability
    for _ in range(5):
        engine.run_cycle()
    assert engine._societies["s1"].stability >= before_stab


def test_civilization_health() -> None:
    from civilization_engine import CivilizationEngine, Society, Institution, InstitutionType
    engine = CivilizationEngine()
    engine.add_society(Society("s1", "Beta", 500))
    engine.add_institution(Institution("sci1", InstitutionType.SCIENCE, "Lab"))
    engine.run_cycle()
    health = engine.civilization_health()
    assert health["cycles"] == 1
    assert health["total_institutions"] == 1


def test_trust_network() -> None:
    from civilization_engine import TrustNetwork
    tn = TrustNetwork()
    tn.set_trust("a", "b", 0.6)
    assert tn.get_trust("a", "b") == 0.6
    tn.update_trust("a", "b", 0.2)
    assert abs(tn.get_trust("a", "b") - 0.8) < 1e-9
