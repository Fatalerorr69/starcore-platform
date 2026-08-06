"""Tests for 18D Universal Language Bridge"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "18D"


def test_concept_registration():
    from language_bridge import UniversalLanguageBridge
    bridge = UniversalLanguageBridge()
    cv = bridge.register("freedom", language="english")
    assert cv.concept == "freedom"
    assert len(cv.embedding) > 0


def test_same_concept_similarity():
    from language_bridge import ConceptVector
    cv = ConceptVector("truth")
    assert abs(cv.similarity(cv) - 1.0) < 1e-6


def test_translation_returns_dict():
    from language_bridge import UniversalLanguageBridge
    bridge = UniversalLanguageBridge()
    bridge.register("love", language="english")
    bridge.register("amour", language="french")
    result = bridge.translate("love", "french")
    assert "source" in result
    assert "translation" in result
    assert "confidence" in result


def test_bridge_stats():
    from language_bridge import UniversalLanguageBridge
    bridge = UniversalLanguageBridge()
    bridge.register("alpha")
    bridge.register("beta")
    stats = bridge.bridge_stats()
    assert stats["concepts"] == 2
    assert stats["translations"] == 0
