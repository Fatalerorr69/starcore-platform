"""15I — Planetary AI Network: Global Mesh + Region Coordinator"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import math
import time


class Region(str, Enum):
    EU_WEST = "eu-west"
    EU_CENTRAL = "eu-central"
    US_EAST = "us-east"
    US_WEST = "us-west"
    APAC = "apac"
    LATAM = "latam"
    AFRICA = "africa"
    MEA = "mea"
    LOCAL = "local"


class DataSovereignty(str, Enum):
    UNRESTRICTED = "unrestricted"
    REGION_ONLY = "region_only"
    COUNTRY_ONLY = "country_only"
    ON_PREMISE = "on_premise"


@dataclass
class PlanetaryNode:
    node_id: str
    region: Region
    sovereignty: DataSovereignty = DataSovereignty.UNRESTRICTED
    lat: float = 0.0
    lon: float = 0.0
    capacity_units: float = 100.0
    load: float = 0.0
    online: bool = True
    last_seen: float = field(default_factory=time.time)

    def latency_to(self, other: "PlanetaryNode") -> float:
        """Approximate latency in ms based on great-circle distance."""
        r = 6371.0
        dlat = math.radians(other.lat - self.lat)
        dlon = math.radians(other.lon - self.lon)
        a = (math.sin(dlat / 2) ** 2
             + math.cos(math.radians(self.lat))
             * math.cos(math.radians(other.lat))
             * math.sin(dlon / 2) ** 2)
        dist_km = 2 * r * math.asin(math.sqrt(a))
        return dist_km / 200.0 * 10.0  # ~10ms per 200km


class PlanetaryMesh:
    def __init__(self) -> None:
        self._nodes: dict[str, PlanetaryNode] = {}
        self._routes: dict[tuple[str, str], float] = {}  # (a,b) -> latency ms

    def register_node(self, node: PlanetaryNode) -> None:
        self._nodes[node.node_id] = node
        for other_id, other in self._nodes.items():
            if other_id != node.node_id:
                lat = node.latency_to(other)
                self._routes[(node.node_id, other_id)] = lat
                self._routes[(other_id, node.node_id)] = lat

    def nearest(self, source_id: str, sovereignty: DataSovereignty | None = None) -> PlanetaryNode | None:
        source = self._nodes.get(source_id)
        if not source:
            return None
        candidates = [
            n for n in self._nodes.values()
            if n.node_id != source_id
            and n.online
            and (sovereignty is None or n.sovereignty == sovereignty)
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda n: self._routes.get((source_id, n.node_id), float("inf")))

    def route_task(self, source_id: str, required_capacity: float,
                   sovereignty: DataSovereignty = DataSovereignty.UNRESTRICTED) -> PlanetaryNode | None:
        source = self._nodes.get(source_id)
        if not source:
            return None
        eligible = [
            n for n in self._nodes.values()
            if n.node_id != source_id
            and n.online
            and (n.capacity_units - n.load) >= required_capacity
            and (sovereignty == DataSovereignty.UNRESTRICTED or n.sovereignty == sovereignty)
        ]
        if not eligible:
            return None
        return min(eligible, key=lambda n: self._routes.get((source_id, n.node_id), float("inf")))

    def global_health(self) -> dict[str, Any]:
        online = [n for n in self._nodes.values() if n.online]
        total_cap = sum(n.capacity_units for n in online)
        total_load = sum(n.load for n in online)
        return {
            "total_nodes": len(self._nodes),
            "online_nodes": len(online),
            "regions": list({n.region.value for n in online}),
            "total_capacity": total_cap,
            "total_load": total_load,
            "utilization_pct": (total_load / total_cap * 100) if total_cap else 0,
            "status": "healthy" if len(online) >= len(self._nodes) * 0.8 else "degraded",
        }
