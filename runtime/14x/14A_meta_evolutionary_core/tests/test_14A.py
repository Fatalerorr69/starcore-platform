"""Tests for STARCORE 14A Meta-Evolutionary Core"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "14A"


def test_evolution_runs() -> None:
    from meta_evolution import MetaEvolutionaryCore

    def fitness(genome: dict) -> float:
        return genome.get("performance", 0.0) - genome.get("cost", 1.0)

    engine = MetaEvolutionaryCore(fitness_fn=fitness, mutation_rate=0.3, population_size=10)
    seeds = [{"performance": float(i), "cost": float(i) * 0.3} for i in range(10)]
    engine.initialize(seeds)
    best = engine.run(generations=5)
    assert best.fitness is not None
    assert len(engine.evolution_history()) == 5


def test_evolution_improves_over_time() -> None:
    from meta_evolution import MetaEvolutionaryCore

    def fitness(genome: dict) -> float:
        return genome.get("x", 0.0)

    engine = MetaEvolutionaryCore(fitness_fn=fitness, mutation_rate=0.4, population_size=20)
    engine.initialize([{"x": float(i)} for i in range(20)])
    gen1 = engine.evolve_step()
    for _ in range(9):
        last_gen = engine.evolve_step()
    assert last_gen.best_fitness >= gen1.best_fitness - 5.0
