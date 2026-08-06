"""Tests for 16G Infinite Scalability Layer"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "16G"


def test_consistent_hashing_stable() -> None:
    from infinite_scale import InfiniteScaler, ShardNode
    scaler = InfiniteScaler()
    for i in range(3):
        scaler.add_node(ShardNode(f"node{i}"))
    node1 = scaler.route("my-key")
    node2 = scaler.route("my-key")
    assert node1 == node2  # deterministic


def test_add_remove_nodes() -> None:
    from infinite_scale import InfiniteScaler, ShardNode
    scaler = InfiniteScaler()
    scaler.add_node(ShardNode("n1"))
    scaler.add_node(ShardNode("n2"))
    assert scaler.cluster_health()["nodes"] == 2
    scaler.remove_node("n1")
    assert scaler.cluster_health()["nodes"] == 1


def test_autoscale_triggers_on_overload() -> None:
    from infinite_scale import InfiniteScaler, ShardNode
    scaler = InfiniteScaler()
    for i in range(3):
        scaler.add_node(ShardNode(f"n{i}", capacity=0.9))  # all overloaded
    before = scaler.cluster_health()["nodes"]
    event = scaler.autoscale()
    assert event is not None
    assert scaler.cluster_health()["nodes"] > before


def test_no_scale_when_healthy() -> None:
    from infinite_scale import InfiniteScaler, ShardNode
    scaler = InfiniteScaler()
    scaler.add_node(ShardNode("n1", capacity=0.3))
    scaler.add_node(ShardNode("n2", capacity=0.4))
    event = scaler.autoscale()
    assert event is None


def test_cluster_health_empty() -> None:
    from infinite_scale import InfiniteScaler
    scaler = InfiniteScaler()
    health = scaler.cluster_health()
    assert health["nodes"] == 0
