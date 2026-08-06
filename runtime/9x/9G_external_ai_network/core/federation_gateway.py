"""9G — External AI Network: Federation Gateway"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NetworkTrust(str, Enum):
    TRUSTED = "trusted"
    VERIFIED = "verified"
    UNTRUSTED = "untrusted"
    BLOCKED = "blocked"


@dataclass
class ExternalNode:
    node_id: str
    endpoint: str
    capabilities: list[str] = field(default_factory=list)
    trust: NetworkTrust = NetworkTrust.UNTRUSTED
    api_version: str = "v1"
    metadata: dict[str, Any] = field(default_factory=dict)


class FederationGateway:
    def __init__(self) -> None:
        self._nodes: dict[str, ExternalNode] = {}
        self._request_log: list[dict[str, Any]] = []

    def register_node(self, node: ExternalNode) -> None:
        self._nodes[node.node_id] = node

    def trust_node(self, node_id: str, level: NetworkTrust) -> None:
        if node_id in self._nodes:
            self._nodes[node_id].trust = level

    def route(self, capability: str) -> list[ExternalNode]:
        return [
            n for n in self._nodes.values()
            if capability in n.capabilities
            and n.trust in (NetworkTrust.TRUSTED, NetworkTrust.VERIFIED)
        ]

    def normalize_request(self, raw: dict[str, Any], target_version: str = "v1") -> dict[str, Any]:
        return {
            "version": target_version,
            "payload": raw,
            "source": "starcore-9g",
        }

    def stats(self) -> dict[str, Any]:
        trust_counts: dict[str, int] = {}
        for n in self._nodes.values():
            trust_counts[n.trust.value] = trust_counts.get(n.trust.value, 0) + 1
        return {"nodes": len(self._nodes), "trust_distribution": trust_counts}
