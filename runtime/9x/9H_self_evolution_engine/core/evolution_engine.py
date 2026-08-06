"""9H — Self Evolution Engine"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
import copy
import random


@dataclass
class Individual:
    genome: dict[str, Any]
    fitness: float = 0.0
    generation: int = 0
    lineage: list[str] = field(default_factory=list)


class EvolutionEngine:
    def __init__(
        self,
        fitness_fn: Callable[[dict[str, Any]], float],
        mutation_rate: float = 0.1,
        population_size: int = 50,
    ) -> None:
        self._fitness_fn = fitness_fn
        self._mutation_rate = mutation_rate
        self._population_size = population_size
        self._population: list[Individual] = []
        self._generation = 0

    def seed(self, genomes: list[dict[str, Any]]) -> None:
        self._population = [Individual(genome=g) for g in genomes]
        self._evaluate()

    def _evaluate(self) -> None:
        for ind in self._population:
            ind.fitness = self._fitness_fn(ind.genome)

    def _mutate(self, genome: dict[str, Any]) -> dict[str, Any]:
        mutated = copy.deepcopy(genome)
        for key in list(mutated.keys()):
            if random.random() < self._mutation_rate:
                val = mutated[key]
                if isinstance(val, (int, float)):
                    mutated[key] = val * (1 + random.gauss(0, 0.1))
                elif isinstance(val, bool):
                    mutated[key] = not val
        return mutated

    def evolve(self, generations: int = 10) -> Individual:
        for _ in range(generations):
            self._population.sort(key=lambda i: i.fitness, reverse=True)
            survivors = self._population[:self._population_size // 2]
            offspring: list[Individual] = []
            while len(offspring) < self._population_size - len(survivors):
                parent = random.choice(survivors)
                child_genome = self._mutate(parent.genome)
                child = Individual(
                    genome=child_genome,
                    generation=self._generation + 1,
                    lineage=parent.lineage + [str(id(parent))],
                )
                offspring.append(child)
            self._population = survivors + offspring
            self._evaluate()
            self._generation += 1
        self._population.sort(key=lambda i: i.fitness, reverse=True)
        return self._population[0]

    def best(self) -> Individual | None:
        if not self._population:
            return None
        return max(self._population, key=lambda i: i.fitness)
