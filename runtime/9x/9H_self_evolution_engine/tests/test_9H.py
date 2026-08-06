"""Tests for 9H Self Evolution Engine"""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "9H"


def test_evolution_improves_fitness() -> None:
    from evolution_engine import EvolutionEngine

    def fitness(genome: dict) -> float:
        return genome.get("speed", 0.0) - genome.get("error_rate", 1.0)

    engine = EvolutionEngine(fitness_fn=fitness, mutation_rate=0.3, population_size=20)
    engine.seed([{"speed": float(i) / 10, "error_rate": 0.5} for i in range(20)])
    best = engine.evolve(generations=5)
    assert best.fitness > -1.0


def test_best_returns_none_before_seed() -> None:
    from evolution_engine import EvolutionEngine
    engine = EvolutionEngine(fitness_fn=lambda g: 0.0)
    assert engine.best() is None
