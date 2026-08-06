"""Tests for STARCORE 12A Cloud Orchestrator"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "12A"


def test_cluster_provisioning() -> None:
    from cloud_orchestrator import CloudOrchestrator, CloudCluster, CloudResource, CloudProvider
    orch = CloudOrchestrator()
    cluster = CloudCluster("c1", "prod-cluster")
    orch.register_cluster(cluster)
    node = CloudResource("node-1", CloudProvider.PROXMOX, "eu-central", "vm", {"cpu": 8, "ram": 32})
    orch.provision("c1", node)
    assert len(cluster.nodes) == 1
    assert cluster.total_capacity("cpu") == 8.0


def test_multi_cloud_balance() -> None:
    from cloud_orchestrator import CloudOrchestrator, CloudCluster, CloudResource, CloudProvider
    orch = CloudOrchestrator()
    cluster = CloudCluster("c1", "hybrid")
    orch.register_cluster(cluster)
    orch.provision("c1", CloudResource("n1", CloudProvider.AWS, "us-east-1", "ec2"))
    orch.provision("c1", CloudResource("n2", CloudProvider.PROXMOX, "local", "vm"))
    balance = orch.multi_cloud_balance()
    assert balance["aws"] == 1
    assert balance["proxmox"] == 1
