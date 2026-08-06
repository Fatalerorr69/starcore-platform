"""Tests for 19E Distributed Wisdom Network"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "19E"


def test_node_contribution():
    from wisdom_network import WisdomNode
    node = WisdomNode("n1", "physics")
    node.contribute("gravity", 9.81)
    assert node.knowledge["gravity"] == 9.81


def test_aggregate_single_node():
    from wisdom_network import DistributedWisdomNetwork, WisdomNode
    net = DistributedWisdomNetwork()
    n = WisdomNode("n1", "science", reliability=1.0)
    n.contribute("pi", 3.14159)
    net.add_node(n)
    result = net.aggregate("pi")
    assert abs(result - 3.14159) < 1e-6


def test_reliability_weighted():
    from wisdom_network import DistributedWisdomNetwork, WisdomNode
    net = DistributedWisdomNetwork()
    n1 = WisdomNode("n1", "a", reliability=0.9)
    n1.contribute("x", 10.0)
    n2 = WisdomNode("n2", "b", reliability=0.1)
    n2.contribute("x", 0.0)
    net.add_node(n1)
    net.add_node(n2)
    result = net.aggregate("x")
    # weighted: (10*0.9 + 0*0.1) / 1.0 = 9.0
    assert result > 5.0  # dominated by high-reliability node


def test_network_stats():
    from wisdom_network import DistributedWisdomNetwork, WisdomNode
    net = DistributedWisdomNetwork()
    net.add_node(WisdomNode("n1", "x"))
    net.add_node(WisdomNode("n2", "y"))
    stats = net.network_stats()
    assert stats["nodes"] == 2
    assert stats["queries"] == 0
