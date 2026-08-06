"""Tests for 18J STARCORE 18 OS Release"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "18J"


def test_boot():
    from starcore_18_os import ApotheosisKernel, ApotheosisPhase
    kernel = ApotheosisKernel()
    result = kernel.boot()
    assert result["status"] == "online"
    assert kernel.phase == ApotheosisPhase.APOTHEOSIS


def test_layers_online():
    from starcore_18_os import ApotheosisKernel
    kernel = ApotheosisKernel()
    kernel.boot()
    assert kernel.system_health()["layers"] == 10


def test_capabilities_active():
    from starcore_18_os import ApotheosisKernel
    kernel = ApotheosisKernel()
    kernel.boot()
    assert kernel.system_health()["capabilities"] == 10


def test_event_log():
    from starcore_18_os import ApotheosisKernel
    kernel = ApotheosisKernel()
    kernel.boot()
    kernel.log_event("test_event")
    assert len(kernel.event_log) >= 2
