"""Tests for 9F Digital Twin Runtime"""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "9F"


def test_twin_state_update() -> None:
    from digital_twin import DigitalTwin
    twin = DigitalTwin("server-01")
    twin.update_real({"cpu": 50, "memory": 70})
    assert twin._real_state.properties["cpu"] == 50


def test_divergence_detection() -> None:
    from digital_twin import DigitalTwin
    twin = DigitalTwin("server-01")
    twin.update_real({"cpu": 50})
    twin.simulate({"cpu": 90})
    diff = twin.divergence()
    assert "cpu" in diff
    assert diff["cpu"]["real"] == 50
    assert diff["cpu"]["simulated"] == 90
