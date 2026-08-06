"""Tests for STARCORE 11B Intent Resolver"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "11B"


def test_intent_resolution() -> None:
    from intent_resolver import IntentResolver, IntentPattern
    resolver = IntentResolver()
    resolver.register(IntentPattern("deploy", ["deploy", "launch", "start"], ["service"]))
    intents = resolver.resolve("please deploy the service now")
    assert len(intents) > 0
    assert intents[0].name == "deploy"


def test_unknown_utterance() -> None:
    from intent_resolver import IntentResolver
    resolver = IntentResolver()
    intents = resolver.resolve("the weather is nice today")
    assert intents == []
