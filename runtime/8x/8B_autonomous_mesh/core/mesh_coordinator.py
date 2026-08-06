"""8B — Autonomous Mesh Coordinator"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import time


@dataclass
class MeshNode:
    node_id: str
    address: str
    capabilities: list[str] = field(default_factory=list)
    last_seen: float = field(default_factory=time.time)
    status: str = "active"


class MeshCoordinator:
    def __init__(self) -> None:
        self._nodes: dict[str, MeshNode] = {}

    def register_node(self, node: MeshNode) -> None:
        self._nodes[node.node_id] = node

    def active_nodes(self) -> list[MeshNode]:
        cutoff = time.time() - 300
        return [n for n in self._nodes.values() if n.last_seen >= cutoff]

    def distribute_task(self, task: dict[str, Any]) -> str | None:
        nodes = self.active_nodes()
        if not nodes:
            return None
        return nodes[0].node_id

    def health(self) -> dict[str, Any]:
        return {"nodes": len(self._nodes), "active": len(self.active_nodes()), "status": "ok"}
