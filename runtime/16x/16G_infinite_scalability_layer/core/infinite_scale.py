"""16G — Infinite Scalability Layer: Consistent-hash ring + elastic autoscaler."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import hashlib
import time


class ScalingStrategy(str, Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    ELASTIC = "elastic"
    PREDICTIVE = "predictive"


@dataclass
class ShardNode:
    node_id: str
    capacity: float = 0.0
    replicas: int = 1
    region: str = "default"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_overloaded(self) -> bool:
        return self.capacity > 0.85


@dataclass
class ScalingEvent:
    event_id: str
    strategy: ScalingStrategy
    from_nodes: int
    to_nodes: int
    reason: str
    timestamp: float = field(default_factory=time.time)


class ConsistentHash:
    def __init__(self, replicas: int = 3) -> None:
        self._replicas = replicas
        self._ring: dict[int, str] = {}
        self._nodes: list[str] = []

    def add_node(self, node_id: str) -> None:
        self._nodes.append(node_id)
        for i in range(self._replicas):
            key = int(hashlib.md5(f"{node_id}:{i}".encode()).hexdigest(), 16)
            self._ring[key] = node_id

    def remove_node(self, node_id: str) -> None:
        self._nodes = [n for n in self._nodes if n != node_id]
        self._ring = {k: v for k, v in self._ring.items() if v != node_id}

    def get_node(self, key: str) -> str | None:
        if not self._ring:
            return None
        h = int(hashlib.md5(key.encode()).hexdigest(), 16)
        sorted_keys = sorted(self._ring.keys())
        for ring_key in sorted_keys:
            if h <= ring_key:
                return self._ring[ring_key]
        return self._ring[sorted_keys[0]]


class InfiniteScaler:
    def __init__(self, strategy: ScalingStrategy = ScalingStrategy.ELASTIC) -> None:
        self._strategy = strategy
        self._nodes: dict[str, ShardNode] = {}
        self._hash_ring = ConsistentHash()
        self._events: list[ScalingEvent] = []

    def add_node(self, node: ShardNode) -> None:
        self._nodes[node.node_id] = node
        self._hash_ring.add_node(node.node_id)

    def remove_node(self, node_id: str) -> None:
        self._nodes.pop(node_id, None)
        self._hash_ring.remove_node(node_id)

    def route(self, key: str) -> str | None:
        return self._hash_ring.get_node(key)

    def autoscale(self) -> ScalingEvent | None:
        if not self._nodes:
            return None
        overloaded = [n for n in self._nodes.values() if n.is_overloaded]
        if len(overloaded) > len(self._nodes) * 0.5:
            new_id = f"node_{len(self._nodes) + 1}"
            self.add_node(ShardNode(node_id=new_id, capacity=0.0))
            event = ScalingEvent(
                event_id=f"scale_{int(time.time())}",
                strategy=self._strategy,
                from_nodes=len(self._nodes) - 1,
                to_nodes=len(self._nodes),
                reason="overload_detected",
            )
            self._events.append(event)
            return event
        return None

    def cluster_health(self) -> dict[str, Any]:
        if not self._nodes:
            return {"nodes": 0, "avg_capacity": 0.0, "overloaded": 0}
        avg_cap = sum(n.capacity for n in self._nodes.values()) / len(self._nodes)
        return {"nodes": len(self._nodes),
                "avg_capacity": round(avg_cap, 4),
                "overloaded": sum(1 for n in self._nodes.values() if n.is_overloaded)}
