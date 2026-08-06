"""Tests for 18H Temporal Causality Resolver"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "18H"


def test_consistent_chain():
    from temporal_causality import TemporalCausalityResolver, CausalEvent
    resolver = TemporalCausalityResolver()
    resolver.record_event(CausalEvent("e1", timestamp=1.0))
    resolver.record_event(CausalEvent("e2", timestamp=2.0, causes=["e1"]))
    chain = resolver.create_chain("c1", ["e1", "e2"])
    assert chain.is_consistent()


def test_paradox_detection():
    from temporal_causality import TemporalCausalityResolver, CausalEvent
    resolver = TemporalCausalityResolver()
    # e2 claims e3 as cause, but e3 happens after e2 (paradox)
    resolver.record_event(CausalEvent("e2", timestamp=1.0, causes=["e3"]))
    resolver.record_event(CausalEvent("e3", timestamp=2.0))
    resolver.create_chain("c1", ["e2", "e3"])
    assert resolver.detect_paradox("c1")


def test_resolve_returns_dict():
    from temporal_causality import TemporalCausalityResolver, CausalEvent
    resolver = TemporalCausalityResolver()
    resolver.record_event(CausalEvent("e1", timestamp=1.0))
    resolver.create_chain("c1", ["e1"])
    result = resolver.resolve("c1")
    assert "consistent" in result
    assert "paradox" in result


def test_missing_chain_resolve():
    from temporal_causality import TemporalCausalityResolver
    resolver = TemporalCausalityResolver()
    result = resolver.resolve("nonexistent")
    assert result["resolved"] is False


def test_resolver_stats():
    from temporal_causality import TemporalCausalityResolver
    resolver = TemporalCausalityResolver()
    stats = resolver.resolver_stats()
    assert stats["events"] == 0
    assert stats["chains"] == 0
