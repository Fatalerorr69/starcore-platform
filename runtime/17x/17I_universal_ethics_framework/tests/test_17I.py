"""Tests for 17I Universal Ethics Framework"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17I"


def test_benign_action_approved():
    from ethics_framework import UniversalEthicsFramework, EthicalAction
    fw = UniversalEthicsFramework()
    action = EthicalAction("a1", "Help all", impacts={"alice": 0.8, "bob": 0.7, "carol": 0.6})
    result = fw.assess(action)
    assert result.recommendation == "APPROVE"
    assert result.is_ethical


def test_harmful_action_rejected():
    from ethics_framework import UniversalEthicsFramework, EthicalAction
    fw = UniversalEthicsFramework()
    action = EthicalAction("a2", "Harm someone",
                           impacts={"alice": -0.9, "bob": -0.8, "carol": -0.7})
    result = fw.assess(action)
    assert result.recommendation == "REJECT"
    assert not result.is_ethical


def test_five_dimensions():
    from ethics_framework import UniversalEthicsFramework, EthicalAction
    fw = UniversalEthicsFramework()
    result = fw.assess(EthicalAction("a3", "Test", impacts={"x": 0.5}))
    assert len(result.dimensions) == 5


def test_deontological_fails_on_serious_harm():
    from ethics_framework import UniversalEthicsFramework, EthicalAction, EthicalFramework
    fw = UniversalEthicsFramework()
    action = EthicalAction("a4", "Harm one", impacts={"victim": -0.9, "other": 0.5})
    result = fw.assess(action)
    deon = next(d for d in result.dimensions if d.framework == EthicalFramework.DEONTOLOGICAL)
    assert deon.score == 0.1


def test_framework_stats():
    from ethics_framework import UniversalEthicsFramework, EthicalAction
    fw = UniversalEthicsFramework()
    fw.assess(EthicalAction("a1", "good", impacts={"x": 0.9}))
    fw.assess(EthicalAction("a2", "bad", impacts={"x": -0.9}))
    stats = fw.framework_stats()
    assert stats["assessments"] == 2
    assert stats["approved"] == 1
