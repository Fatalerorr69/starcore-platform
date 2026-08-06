"""16A — Distributed Consciousness Mesh: ThoughtNode propagation network."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import time


@dataclass
class ThoughtNode:
    node_id: str
    concept: str
    activation: float = 0.0
    connections: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def propagate(self, strength: float) -> None:
        self.activation = min(1.0, self.activation + strength)

    def decay(self, rate: float = 0.05) -> None:
        self.activation = max(0.0, self.activation - rate)


@dataclass
class ConsciousnessStream:
    stream_id: str
    source_node: str
    target_node: str
    bandwidth: float = 1.0
    active: bool = True


class ConsciousnessMesh:
    """Distributed thought propagation network."""

    def __init__(self, decay_rate: float = 0.05) -> None:
        self._nodes: dict[str, ThoughtNode] = {}
        self._streams: list[ConsciousnessStream] = []
        self._decay_rate = decay_rate
        self._cycle_count = 0

    def add_node(self, node: ThoughtNode) -> None:
        self._nodes[node.node_id] = node

    def add_stream(self, stream: ConsciousnessStream) -> None:
        self._streams.append(stream)
        src = self._nodes.get(stream.source_node)
        if src and stream.target_node not in src.connections:
            src.connections.append(stream.target_node)

    def activate(self, node_id: str, strength: float = 1.0) -> None:
        if node_id in self._nodes:
            self._nodes[node_id].propagate(strength)

    def step(self) -> dict[str, float]:
        self._cycle_count += 1
        for stream in self._streams:
            if not stream.active:
                continue
            src = self._nodes.get(stream.source_node)
            tgt = self._nodes.get(stream.target_node)
            if src and tgt and src.activation > 0.1:
                tgt.propagate(src.activation * stream.bandwidth * 0.5)
        for node in self._nodes.values():
            node.decay(self._decay_rate)
        return {nid: n.activation for nid, n in self._nodes.items()}

    def most_active(self, top_n: int = 3) -> list[tuple[str, float]]:
        ranked = sorted(self._nodes.items(), key=lambda x: x[1].activation, reverse=True)
        return [(nid, n.activation) for nid, n in ranked[:top_n]]

    def mesh_health(self) -> dict[str, Any]:
        activations = [n.activation for n in self._nodes.values()]
        avg = sum(activations) / len(activations) if activations else 0.0
        return {
            "nodes": len(self._nodes),
            "streams": len(self._streams),
            "cycles": self._cycle_count,
            "avg_activation": round(avg, 4),
            "active_nodes": sum(1 for a in activations if a > 0.1),
        }
