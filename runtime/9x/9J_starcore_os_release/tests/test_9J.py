"""Tests for 9J STARCORE 9 OS Release"""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "9J"
    assert data["version"] == "9.10.0"


def test_os_boot() -> None:
    from starcore_os import StarCoreOS, LayerStatus
    os_ = StarCoreOS()
    for lid in ["9A", "9B", "9C"]:
        os_.register_layer(LayerStatus(lid, f"Layer {lid}", "9.x.0"))
    result = os_.boot()
    assert result["status"] == "running"
    assert result["layers_loaded"] == 3


def test_system_health() -> None:
    from starcore_os import StarCoreOS, LayerStatus
    os_ = StarCoreOS()
    os_.register_layer(LayerStatus("9A", "Intelligence Kernel", "9.1.0"))
    os_.boot()
    health = os_.system_health()
    assert health["os"] == "STARCORE 9 OS"
