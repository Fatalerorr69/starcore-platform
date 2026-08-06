"""Tests for 19C Synthetic Evolution Engine"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "19C"


def test_population_initialized():
    from synthetic_evolution import SyntheticEvolutionEngine
    engine = SyntheticEvolutionEngine(pop_size=10, gene_count=3)
    assert len(engine._population) == 10
    assert len(engine._population[0].genes) == 3


def test_evaluate_sets_fitness():
    from synthetic_evolution import SyntheticEvolutionEngine
    engine = SyntheticEvolutionEngine(pop_size=10, gene_count=3)
    engine.evaluate(lambda genes: sum(g * g for g in genes))
    assert engine._best_fitness > 0.0


def test_evolve_increments_generation():
    from synthetic_evolution import SyntheticEvolutionEngine
    engine = SyntheticEvolutionEngine(pop_size=10, gene_count=3)
    engine.evaluate(lambda genes: sum(g * g for g in genes))
    engine.evolve()
    assert engine._generation == 1
    assert len(engine._population) == 10


def test_best_returns_fittest():
    from synthetic_evolution import SyntheticEvolutionEngine, Chromosome
    engine = SyntheticEvolutionEngine(pop_size=5, gene_count=2)
    engine.evaluate(lambda genes: sum(genes))
    best = engine.best()
    assert isinstance(best, Chromosome)
    assert best.fitness == max(c.fitness for c in engine._population)
