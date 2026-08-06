"""Tests for 15I Planetary AI Network"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "15I"


def test_node_registration_and_routing() -> None:
    from planetary_network import PlanetaryMesh, PlanetaryNode, Region, DataSovereignty
    mesh = PlanetaryMesh()
    eu = PlanetaryNode("eu-1", Region.EU_CENTRAL, lat=50.1, lon=8.7, capacity_units=100.0, load=10.0)
    us = PlanetaryNode("us-1", Region.US_EAST, lat=40.7, lon=-74.0, capacity_units=100.0, load=50.0)
    mesh.register_node(eu)
    mesh.register_node(us)
    target = mesh.route_task("eu-1", required_capacity=40.0)
    assert target is not None
    assert target.node_id == "us-1"


def test_latency_calculation() -> None:
    from planetary_network import PlanetaryNode, Region
    eu = PlanetaryNode("eu", Region.EU_CENTRAL, lat=50.0, lon=10.0)
    us = PlanetaryNode("us", Region.US_EAST, lat=40.0, lon=-74.0)
    latency = eu.latency_to(us)
    assert latency > 30.0  # transatlantic should be > 30ms


def test_sovereignty_filtering() -> None:
    from planetary_network import PlanetaryMesh, PlanetaryNode, Region, DataSovereignty
    mesh = PlanetaryMesh()
    eu = PlanetaryNode("eu-src", Region.EU_CENTRAL, lat=50.0, lon=8.0, capacity_units=100.0, load=0.0)
    us = PlanetaryNode("us-1", Region.US_EAST, lat=40.0, lon=-74.0,
                       sovereignty=DataSovereignty.COUNTRY_ONLY, capacity_units=100.0, load=0.0)
    eu_only = PlanetaryNode("eu-2", Region.EU_WEST, lat=48.0, lon=2.0,
                            sovereignty=DataSovereignty.REGION_ONLY, capacity_units=100.0, load=0.0)
    mesh.register_node(eu)
    mesh.register_node(us)
    mesh.register_node(eu_only)
    target = mesh.route_task("eu-src", 10.0, DataSovereignty.REGION_ONLY)
    assert target is not None
    assert target.node_id == "eu-2"


def test_global_health() -> None:
    from planetary_network import PlanetaryMesh, PlanetaryNode, Region
    mesh = PlanetaryMesh()
    for i in range(3):
        mesh.register_node(PlanetaryNode(f"n{i}", Region.EU_CENTRAL,
                                         lat=50.0 + i, lon=10.0 + i,
                                         capacity_units=100.0, load=30.0))
    health = mesh.global_health()
    assert health["total_nodes"] == 3
    assert health["status"] == "healthy"
