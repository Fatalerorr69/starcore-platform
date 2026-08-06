"""Tests for 16J STARCORE 16 OS Release — TranscendenceKernel"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "16J"


def test_transcendence_boot() -> None:
    from starcore_16_os import TranscendenceKernel, TranscendencePhase
    kernel = TranscendenceKernel()
    state = kernel.boot()
    assert state.phase == TranscendencePhase.ACTIVE
    assert state.version == "16.10.0"
    assert state.codename == "TRANSCENDENCE"


def test_capabilities_active_after_boot() -> None:
    from starcore_16_os import TranscendenceKernel, STARCORE_16_CAPABILITIES
    kernel = TranscendenceKernel()
    kernel.boot()
    health = kernel.system_health()
    assert health["capabilities"] == len(STARCORE_16_CAPABILITIES)


def test_layers_online_after_boot() -> None:
    from starcore_16_os import TranscendenceKernel, STARCORE_16_LAYERS
    kernel = TranscendenceKernel()
    kernel.boot()
    health = kernel.system_health()
    assert health["layers_online"] == len(STARCORE_16_LAYERS)


def test_event_log_populated() -> None:
    from starcore_16_os import TranscendenceKernel
    kernel = TranscendenceKernel()
    kernel.boot()
    log = kernel.event_log()
    assert len(log) > 0
    events = [e["event"] for e in log]
    assert "transcendence_kernel_active" in events
