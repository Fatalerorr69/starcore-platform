"""STARCORE 12A — Cloud Network Fabric: Cloud Orchestrator"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CloudProvider(str, Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    HETZNER = "hetzner"
    PROXMOX = "proxmox"
    BARE_METAL = "bare_metal"


@dataclass
class CloudResource:
    resource_id: str
    provider: CloudProvider
    region: str
    resource_type: str
    specs: dict[str, Any] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
    status: str = "running"


@dataclass
class CloudCluster:
    cluster_id: str
    name: str
    nodes: list[CloudResource] = field(default_factory=list)
    primary_provider: CloudProvider = CloudProvider.PROXMOX

    def add_node(self, node: CloudResource) -> None:
        self.nodes.append(node)

    def nodes_by_provider(self, provider: CloudProvider) -> list[CloudResource]:
        return [n for n in self.nodes if n.provider == provider]

    def total_capacity(self, spec_key: str) -> float:
        return sum(float(n.specs.get(spec_key, 0)) for n in self.nodes)


class CloudOrchestrator:
    def __init__(self) -> None:
        self._clusters: dict[str, CloudCluster] = {}
        self._resources: dict[str, CloudResource] = {}

    def register_cluster(self, cluster: CloudCluster) -> None:
        self._clusters[cluster.cluster_id] = cluster

    def provision(self, cluster_id: str, resource: CloudResource) -> CloudResource:
        cluster = self._clusters.get(cluster_id)
        if cluster:
            cluster.add_node(resource)
        self._resources[resource.resource_id] = resource
        return resource

    def multi_cloud_balance(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in self._resources.values():
            counts[r.provider.value] = counts.get(r.provider.value, 0) + 1
        return counts
