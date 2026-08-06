"""Tests for 19B Cognitive Load Balancer"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "19B"


def test_task_submitted_to_channel():
    from cognitive_load import CognitiveLoadBalancer, CognitiveTask
    balancer = CognitiveLoadBalancer(num_channels=2)
    task = CognitiveTask("t1", "think", cognitive_cost=0.3)
    ch_id = balancer.submit(task)
    assert ch_id is not None
    assert balancer._processed == 1


def test_overloaded_returns_none():
    from cognitive_load import CognitiveLoadBalancer, CognitiveTask, CognitiveChannel
    balancer = CognitiveLoadBalancer(num_channels=1)
    balancer._channels[0].current_load = 1.0  # full
    task = CognitiveTask("t1", "heavy", cognitive_cost=0.5)
    result = balancer.submit(task)
    assert result is None


def test_complete_reduces_load():
    from cognitive_load import CognitiveChannel, CognitiveTask
    ch = CognitiveChannel("ch0", max_load=1.0)
    task = CognitiveTask("t1", "work", cognitive_cost=0.4)
    ch.accept(task)
    assert ch.current_load == 0.4
    ch.complete("t1")
    assert ch.current_load == 0.0


def test_balancer_stats():
    from cognitive_load import CognitiveLoadBalancer
    balancer = CognitiveLoadBalancer(num_channels=3)
    stats = balancer.balancer_stats()
    assert stats["channels"] == 3
    assert stats["processed"] == 0
