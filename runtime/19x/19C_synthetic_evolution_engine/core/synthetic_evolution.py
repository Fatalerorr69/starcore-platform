"""19C — Synthetic Evolution Engine: genetic algorithm with tournament selection."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
import random


@dataclass
class Chromosome:
    genes: list[float]
    fitness: float = 0.0

    def mutate(self, rate: float = 0.1, scale: float = 0.1) -> "Chromosome":
        new_genes = [
            g + random.gauss(0, scale) if random.random() < rate else g
            for g in self.genes
        ]
        return Chromosome(genes=new_genes)

    def crossover(self, other: "Chromosome") -> tuple["Chromosome", "Chromosome"]:
        if len(self.genes) < 2:
            return Chromosome(genes=list(self.genes)), Chromosome(genes=list(other.genes))
        point = random.randint(1, len(self.genes) - 1)
        return (
            Chromosome(genes=self.genes[:point] + other.genes[point:]),
            Chromosome(genes=other.genes[:point] + self.genes[point:]),
        )


class SyntheticEvolutionEngine:
    def __init__(self, pop_size: int = 20, gene_count: int = 5) -> None:
        self._pop_size = pop_size
        self._gene_count = gene_count
        self._population: list[Chromosome] = [
            Chromosome(genes=[random.uniform(-1.0, 1.0) for _ in range(gene_count)])
            for _ in range(pop_size)
        ]
        self._generation: int = 0
        self._best_fitness: float = float("-inf")

    def evaluate(self, fitness_fn: Callable[[list[float]], float]) -> None:
        for chrom in self._population:
            chrom.fitness = fitness_fn(chrom.genes)
        best = max(self._population, key=lambda c: c.fitness)
        self._best_fitness = best.fitness

    def evolve(self) -> None:
        self._population.sort(key=lambda c: c.fitness, reverse=True)
        elite = self._population[:2]
        new_pop: list[Chromosome] = list(elite)
        pool = self._population[:max(2, min(10, len(self._population)))]
        while len(new_pop) < self._pop_size:
            p1, p2 = random.sample(pool, 2)
            c1, c2 = p1.crossover(p2)
            new_pop.extend([c1.mutate(), c2.mutate()])
        self._population = new_pop[:self._pop_size]
        self._generation += 1

    def best(self) -> Chromosome:
        return max(self._population, key=lambda c: c.fitness)

    def evolution_stats(self) -> dict[str, Any]:
        return {
            "generation": self._generation,
            "population": len(self._population),
            "best_fitness": round(self._best_fitness, 4),
        }
