"""Tests for 16H Universal Knowledge Graph"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "16H"


def test_add_concepts_and_relations() -> None:
    from knowledge_graph import KnowledgeGraph, Concept, Relation
    kg = KnowledgeGraph()
    kg.add_concept(Concept("ai", "Artificial Intelligence"))
    kg.add_concept(Concept("ml", "Machine Learning"))
    kg.add_relation(Relation("r1", "ml", "ai", "is_a"))
    stats = kg.graph_stats()
    assert stats["concepts"] == 2
    assert stats["relations"] == 1


def test_shortest_path() -> None:
    from knowledge_graph import KnowledgeGraph, Concept, Relation
    kg = KnowledgeGraph()
    for cid in ["a", "b", "c"]:
        kg.add_concept(Concept(cid, cid))
    kg.add_relation(Relation("r1", "a", "b", "related_to"))
    kg.add_relation(Relation("r2", "b", "c", "related_to"))
    path = kg.shortest_path("a", "c")
    assert path == ["a", "b", "c"]


def test_no_path_returns_empty() -> None:
    from knowledge_graph import KnowledgeGraph, Concept
    kg = KnowledgeGraph()
    kg.add_concept(Concept("x", "X"))
    kg.add_concept(Concept("y", "Y"))
    path = kg.shortest_path("x", "y")
    assert path == []


def test_semantic_similarity() -> None:
    from knowledge_graph import KnowledgeGraph, Concept
    kg = KnowledgeGraph()
    kg.add_concept(Concept("c1", "cat", embedding=[1.0, 0.0, 0.0]))
    kg.add_concept(Concept("c2", "kitten", embedding=[0.9, 0.1, 0.0]))
    kg.add_concept(Concept("c3", "car", embedding=[0.0, 0.0, 1.0]))
    sim_close = kg.semantic_similarity("c1", "c2")
    sim_far = kg.semantic_similarity("c1", "c3")
    assert sim_close > sim_far


def test_neighbors_by_type() -> None:
    from knowledge_graph import KnowledgeGraph, Concept, Relation
    kg = KnowledgeGraph()
    for cid in ["a", "b", "c"]:
        kg.add_concept(Concept(cid, cid))
    kg.add_relation(Relation("r1", "a", "b", "is_a"))
    kg.add_relation(Relation("r2", "a", "c", "has_part"))
    assert "b" in kg.neighbors("a", "is_a")
    assert "c" not in kg.neighbors("a", "is_a")
