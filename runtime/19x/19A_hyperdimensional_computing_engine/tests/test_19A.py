"""Tests for 19A Hyperdimensional Computing Engine"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "19A"


def test_encode_creates_vector():
    from hyperdimensional import HyperdimensionalComputer
    hdc = HyperdimensionalComputer(dim=256)
    hv = hdc.encode("apple")
    assert hv.name == "apple"
    assert len(hv.bits) == 256


def test_self_similarity_is_one():
    from hyperdimensional import HyperVector
    hv = HyperVector("a", _dim=256)
    assert hv.similarity(hv) == 1.0


def test_bind_changes_vector():
    from hyperdimensional import HyperVector
    a = HyperVector("a", _dim=256)
    b = HyperVector("b", _dim=256)
    bound = a.bind(b)
    # XOR result should be less similar to original than self
    assert bound.similarity(a) < 1.0


def test_superpose_identical():
    from hyperdimensional import HyperVector
    hv = HyperVector("x", bits=[1, 0, 1, 0, 1])
    result = HyperVector.superpose(hv, hv)
    assert result.bits == hv.bits
