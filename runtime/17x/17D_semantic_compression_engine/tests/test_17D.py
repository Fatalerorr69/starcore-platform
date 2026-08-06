"""Tests for 17D Semantic Compression Engine"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17D"


def test_compress_produces_unit_vector():
    from semantic_compression import SemanticCompressor
    import math
    sc = SemanticCompressor(code_dim=16)
    code = sc.compress("hello world")
    norm = math.sqrt(sum(v ** 2 for v in code.compressed))
    assert abs(norm - 1.0) < 1e-6


def test_same_content_same_id():
    from semantic_compression import SemanticCompressor
    sc = SemanticCompressor()
    c1 = sc.compress("deterministic content")
    c2 = sc.compress("deterministic content")
    assert c1.code_id == c2.code_id


def test_similarity_identical():
    from semantic_compression import SemanticCompressor
    sc = SemanticCompressor()
    c = sc.compress("test phrase")
    assert abs(sc.similarity(c, c) - 1.0) < 1e-6


def test_search_finds_stored():
    from semantic_compression import SemanticCompressor
    sc = SemanticCompressor()
    sc.compress("machine learning", tags=["ai"])
    sc.compress("quantum physics", tags=["science"])
    results = sc.search("machine learning", top_k=1)
    assert len(results) == 1
    assert results[0][0] == sc.compress("machine learning").code_id
