"""15C — Universal Connector Fabric: Protocol Adapter & Semantic Router"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable
import uuid


class Protocol(str, Enum):
    REST = "rest"
    GRPC = "grpc"
    MQTT = "mqtt"
    WEBSOCKET = "websocket"
    STARCORE_INTERNAL = "starcore_internal"
    CUSTOM = "custom"


@dataclass
class ConnectorSpec:
    connector_id: str = field(default_factory=lambda: str(uuid.uuid4())[:10])
    name: str = ""
    protocol: Protocol = Protocol.REST
    endpoint: str = ""
    schema_version: str = "v1"
    transform: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    capabilities: list[str] = field(default_factory=list)
    active: bool = True


@dataclass
class NormalizedEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    source_connector: str = ""
    event_type: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    schema_version: str = "v1"
    routed_to: list[str] = field(default_factory=list)


class UniversalConnectorFabric:
    """Adapts any external protocol/schema into STARCORE's internal event model."""

    def __init__(self) -> None:
        self._connectors: dict[str, ConnectorSpec] = {}
        self._routes: dict[str, list[str]] = {}  # event_type -> [connector_ids]
        self._event_log: list[NormalizedEvent] = []

    def register(self, spec: ConnectorSpec) -> None:
        self._connectors[spec.connector_id] = spec

    def route(self, event_type: str, connector_ids: list[str]) -> None:
        self._routes[event_type] = connector_ids

    def ingest(self, raw: dict[str, Any], source_id: str, event_type: str) -> NormalizedEvent:
        connector = self._connectors.get(source_id)
        payload = raw
        if connector and connector.transform:
            payload = connector.transform(raw)

        event = NormalizedEvent(
            source_connector=source_id,
            event_type=event_type,
            payload=payload,
        )
        targets = self._routes.get(event_type, [])
        event.routed_to = [t for t in targets if t in self._connectors
                           and self._connectors[t].active]
        self._event_log.append(event)
        return event

    def schema_normalize(self, data: dict[str, Any], target_schema: dict[str, str]) -> dict[str, Any]:
        """Map data keys to target schema field names."""
        result: dict[str, Any] = {}
        for src_key, tgt_key in target_schema.items():
            if src_key in data:
                result[tgt_key] = data[src_key]
        return result

    def active_connectors(self, protocol: Protocol | None = None) -> list[ConnectorSpec]:
        connectors = [c for c in self._connectors.values() if c.active]
        if protocol:
            connectors = [c for c in connectors if c.protocol == protocol]
        return connectors

    def fabric_stats(self) -> dict[str, Any]:
        proto_counts: dict[str, int] = {}
        for c in self._connectors.values():
            proto_counts[c.protocol.value] = proto_counts.get(c.protocol.value, 0) + 1
        return {
            "connectors": len(self._connectors),
            "routes": len(self._routes),
            "events_processed": len(self._event_log),
            "protocols": proto_counts,
        }
