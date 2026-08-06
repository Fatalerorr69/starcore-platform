"""Tests for 9G External AI Network"""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "9G"


def test_node_routing() -> None:
    from federation_gateway import FederationGateway, ExternalNode, NetworkTrust
    gw = FederationGateway()
    gw.register_node(ExternalNode("node-1", "https://ai.example.com", ["nlp", "vision"], NetworkTrust.TRUSTED))
    gw.register_node(ExternalNode("node-2", "https://ai2.example.com", ["nlp"], NetworkTrust.UNTRUSTED))
    results = gw.route("nlp")
    assert len(results) == 1
    assert results[0].node_id == "node-1"
