"""Tests for 19J STARCORE 19 OS Release"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "19J"


def test_boot():
    from starcore_19_os import OmniscienceKernel, OmnisciencePhase
    kernel = OmniscienceKernel()
    result = kernel.boot()
    assert result["status"] == "online"
    assert kernel.phase == OmnisciencePhase.OMNISCIENCE


def test_layers_count():
    from starcore_19_os import OmniscienceKernel
    kernel = OmniscienceKernel()
    kernel.boot()
    assert kernel.system_health()["layers"] == 10


def test_capabilities_count():
    from starcore_19_os import OmniscienceKernel
    kernel = OmniscienceKernel()
    kernel.boot()
    assert kernel.system_health()["capabilities"] == 10


def test_event_log():
    from starcore_19_os import OmniscienceKernel
    kernel = OmniscienceKernel()
    kernel.boot()
    kernel.log_event("test_event")
    assert len(kernel.event_log) >= 2
