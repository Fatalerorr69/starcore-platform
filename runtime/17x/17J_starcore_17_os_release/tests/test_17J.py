"""Tests for 17J STARCORE 17 OS — SingularityKernel"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17J"


def test_singularity_boot():
    from starcore_17_os import SingularityKernel, SingularityPhase
    k = SingularityKernel()
    state = k.boot()
    assert state.phase == SingularityPhase.ACTIVE
    assert state.codename == "SINGULARITY"


def test_capabilities_active():
    from starcore_17_os import SingularityKernel, STARCORE_17_CAPABILITIES
    k = SingularityKernel()
    k.boot()
    health = k.system_health()
    assert health["capabilities"] == len(STARCORE_17_CAPABILITIES)


def test_layers_online():
    from starcore_17_os import SingularityKernel, STARCORE_17_LAYERS
    k = SingularityKernel()
    k.boot()
    health = k.system_health()
    assert health["layers_online"] == len(STARCORE_17_LAYERS)


def test_event_log():
    from starcore_17_os import SingularityKernel
    k = SingularityKernel()
    k.boot()
    log = k.event_log()
    assert any(e["event"] == "singularity_kernel_active" for e in log)
