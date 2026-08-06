"""Tests for 8C Security Fabric"""
from pathlib import Path
import json


def test_manifest_layer() -> None:
    p = Path(__file__).parent.parent / "registry" / "manifest.json"
    data = json.loads(p.read_text())
    assert data["layer"] == "8C"


def test_health_status() -> None:
    p = Path(__file__).parent.parent / "runtime" / "health.json"
    data = json.loads(p.read_text())
    assert data["status"] == "healthy"
