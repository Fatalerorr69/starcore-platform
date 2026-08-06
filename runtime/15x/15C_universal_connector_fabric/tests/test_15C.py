"""Tests for 15C Universal Connector Fabric"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "15C"


def test_connector_registration_and_ingest() -> None:
    from universal_connector import UniversalConnectorFabric, ConnectorSpec, Protocol
    fabric = UniversalConnectorFabric()
    spec = ConnectorSpec(name="prometheus", protocol=Protocol.REST, endpoint="http://prom:9090")
    fabric.register(spec)
    event = fabric.ingest({"metric": "cpu", "value": 0.8}, spec.connector_id, "metric.update")
    assert event.source_connector == spec.connector_id
    assert event.payload["metric"] == "cpu"


def test_routing() -> None:
    from universal_connector import UniversalConnectorFabric, ConnectorSpec, Protocol
    fabric = UniversalConnectorFabric()
    src = ConnectorSpec(name="sensor", protocol=Protocol.MQTT)
    dst = ConnectorSpec(name="processor", protocol=Protocol.STARCORE_INTERNAL)
    fabric.register(src)
    fabric.register(dst)
    fabric.route("sensor.reading", [dst.connector_id])
    event = fabric.ingest({"temp": 22.5}, src.connector_id, "sensor.reading")
    assert dst.connector_id in event.routed_to


def test_schema_normalize() -> None:
    from universal_connector import UniversalConnectorFabric
    fabric = UniversalConnectorFabric()
    raw = {"cpu_pct": 75.0, "mem_pct": 60.0}
    normalized = fabric.schema_normalize(raw, {"cpu_pct": "cpu", "mem_pct": "memory"})
    assert normalized == {"cpu": 75.0, "memory": 60.0}


def test_transform_applied() -> None:
    from universal_connector import UniversalConnectorFabric, ConnectorSpec, Protocol
    fabric = UniversalConnectorFabric()
    spec = ConnectorSpec(
        name="transformer",
        protocol=Protocol.CUSTOM,
        transform=lambda d: {"normalized_value": d.get("raw", 0) / 100.0},
    )
    fabric.register(spec)
    event = fabric.ingest({"raw": 80}, spec.connector_id, "data")
    assert event.payload["normalized_value"] == 0.8
