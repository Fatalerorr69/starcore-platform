"""Tests for 8A AI Core Runtime"""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest_exists() -> None:
    p = Path(__file__).parent.parent / "registry" / "manifest.json"
    assert p.exists(), "manifest.json must exist"
    data = json.loads(p.read_text())
    assert data["layer"] == "8A"
    assert data["status"] == "PRODUCTION"


def test_health_exists() -> None:
    p = Path(__file__).parent.parent / "runtime" / "health.json"
    assert p.exists(), "health.json must exist"
    data = json.loads(p.read_text())
    assert data["status"] == "healthy"


def test_inference_engine() -> None:
    from inference_engine import InferenceEngine, InferenceRequest
    engine = InferenceEngine()
    req = InferenceRequest(model="starcore-8a", prompt="Hello")
    resp = engine.infer(req)
    assert resp.status == "ok"
    assert resp.model == "starcore-8a"
