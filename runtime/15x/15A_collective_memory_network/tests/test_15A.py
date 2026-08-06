"""Tests for 15A Collective Memory Network"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "15A"
    assert data["phase"] == "PHASE_2"


def test_write_and_recall() -> None:
    from collective_memory import CollectiveMemoryNetwork
    net = CollectiveMemoryNetwork()
    frag = net.write("STARCORE 15 launched", "agent-alpha", importance=0.9, tags=["release"])
    results = net.recall("STARCORE")
    assert len(results) == 1
    assert results[0].fragment_id == frag.fragment_id


def test_consensus_voting() -> None:
    from collective_memory import CollectiveMemoryNetwork
    net = CollectiveMemoryNetwork(consensus_threshold=2)
    frag = net.write("critical insight", "agent-a", importance=0.9)
    assert not frag.is_consensus()
    net.vote(frag.fragment_id, "agent-b")
    net.vote(frag.fragment_id, "agent-c")
    assert frag.is_consensus()


def test_author_cannot_self_vote() -> None:
    from collective_memory import CollectiveMemoryNetwork
    net = CollectiveMemoryNetwork()
    frag = net.write("test", "agent-x")
    result = net.vote(frag.fragment_id, "agent-x")
    assert result is False
    assert frag.consensus_votes == 0


def test_cross_agent_sync() -> None:
    from collective_memory import CollectiveMemoryNetwork
    net = CollectiveMemoryNetwork()
    net.write("important fact", "agent-alpha", importance=0.9)
    net.write("minor detail", "agent-alpha", importance=0.3)
    synced = net.cross_agent_sync("agent-alpha", "agent-beta")
    assert synced == 1


def test_tag_recall() -> None:
    from collective_memory import CollectiveMemoryNetwork
    net = CollectiveMemoryNetwork()
    net.write("event A", "a1", tags=["critical"])
    net.write("event B", "a2", tags=["info"])
    results = net.recall("", tag="critical")
    assert len(results) == 1
