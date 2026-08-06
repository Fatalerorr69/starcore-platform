"""Tests for 15J STARCORE 15 OS Release"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "15J"
    assert data["version"] == "15.10.0"


def test_nexus_boot() -> None:
    from starcore_15_os import NexusKernel, NexusLayerStatus, STARCORE_15_LAYERS
    kernel = NexusKernel()
    for lid in STARCORE_15_LAYERS:
        kernel.register_layer(NexusLayerStatus(lid, f"Layer {lid}", "15.x.0"))
    state = kernel.boot()
    assert state.status == "running"
    assert state.layers_loaded == 10
    assert state.codename == "NEXUS"


def test_capabilities_active_after_boot() -> None:
    from starcore_15_os import NexusKernel, NexusLayerStatus, STARCORE_15_CAPABILITIES
    kernel = NexusKernel()
    kernel.register_layer(NexusLayerStatus("15A", "Collective Memory", "15.1.0"))
    kernel.boot()
    health = kernel.system_health()
    assert health["capabilities"] == len(STARCORE_15_CAPABILITIES)


def test_event_log_populated() -> None:
    from starcore_15_os import NexusKernel, NexusLayerStatus
    kernel = NexusKernel()
    kernel.register_layer(NexusLayerStatus("15A", "Layer A", "15.1.0"))
    kernel.register_layer(NexusLayerStatus("15B", "Layer B", "15.2.0"))
    kernel.boot()
    log = kernel.event_log()
    assert len(log) == 2
    assert all(e["event"] == "layer_loaded" for e in log)
