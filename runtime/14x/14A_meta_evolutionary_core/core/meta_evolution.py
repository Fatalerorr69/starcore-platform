"""STARCORE 14A — Self-Evolving AI Platform: Meta-Evolutionary Core"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
import copy
import random
import time


@dataclass
class EvolutionGeneration:
    generation_id: int
    timestamp: float = field(default_factory=time.time)
    population_size: int = 0
    best_fitness: float = 0.0
    avg_fitness: float = 0.0
    mutations: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ArchitectureBlueprint:
    blueprint_id: str
    components: dict[str, Any]
    fitness: float = 0.0
    generation: int = 0
    parent_ids: list[str] = field(default_factory=list)


class MetaEvolutionaryCore:
    def __init__(
        self,
        fitness_fn: Callable[[dict[str, Any]], float],
        mutation_rate: float = 0.15,
        crossover_rate: float = 0.7,
        population_size: int = 30,
    ) -> None:
        self._fitness_fn = fitness_fn
        self._mutation_rate = mutation_rate
        self._crossover_rate = crossover_rate
        self._population_size = population_size
        self._population: list[ArchitectureBlueprint] = []
        self._generation_log: list[EvolutionGeneration] = []
        self._current_gen = 0

    def initialize(self, seed_blueprints: list[dict[str, Any]]) -> None:
        self._population = [
            ArchitectureBlueprint(
                blueprint_id=f"bp-{i:04d}",
                components=copy.deepcopy(bp),
                fitness=self._fitness_fn(bp),
            )
            for i, bp in enumerate(seed_blueprints)
        ]

    def _mutate(self, blueprint: dict[str, Any]) -> dict[str, Any]:
        mutated = copy.deepcopy(blueprint)
        for key in list(mutated.keys()):
            if random.random() < self._mutation_rate:
                val = mutated[key]
                if isinstance(val, (int, float)):
                    mutated[key] = val * (1 + random.gauss(0, 0.15))
                elif isinstance(val, bool):
                    mutated[key] = not val
                elif isinstance(val, list) and val:
                    idx = random.randint(0, len(val) - 1)
                    mutated[key] = val[:idx] + val[idx + 1:]
        return mutated

    def _crossover(self, a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
        child: dict[str, Any] = {}
        all_keys = set(a) | set(b)
        for key in all_keys:
            if key in a and key in b:
                child[key] = a[key] if random.random() < 0.5 else b[key]
            elif key in a:
                child[key] = a[key]
            else:
                child[key] = b[key]
        return child

    def evolve_step(self) -> EvolutionGeneration:
        self._population.sort(key=lambda bp: bp.fitness, reverse=True)
        elite_count = max(2, self._population_size // 5)
        survivors = self._population[:elite_count]

        new_pop: list[ArchitectureBlueprint] = list(survivors)
        mutations = 0

        while len(new_pop) < self._population_size:
            if random.random() < self._crossover_rate and len(survivors) >= 2:
                p1, p2 = random.sample(survivors, 2)
                child_comps = self._crossover(p1.components, p2.components)
                parent_ids = [p1.blueprint_id, p2.blueprint_id]
            else:
                parent = random.choice(survivors)
                child_comps = parent.components
                parent_ids = [parent.blueprint_id]

            if random.random() < self._mutation_rate:
                child_comps = self._mutate(child_comps)
                mutations += 1

            child = ArchitectureBlueprint(
                blueprint_id=f"bp-{self._current_gen:04d}-{len(new_pop):04d}",
                components=child_comps,
                fitness=self._fitness_fn(child_comps),
                generation=self._current_gen + 1,
                parent_ids=parent_ids,
            )
            new_pop.append(child)

        self._population = new_pop
        self._current_gen += 1

        gen_record = EvolutionGeneration(
            generation_id=self._current_gen,
            population_size=len(self._population),
            best_fitness=max(bp.fitness for bp in self._population),
            avg_fitness=sum(bp.fitness for bp in self._population) / len(self._population),
            mutations=mutations,
        )
        self._generation_log.append(gen_record)
        return gen_record

    def run(self, generations: int) -> ArchitectureBlueprint:
        for _ in range(generations):
            self.evolve_step()
        return max(self._population, key=lambda bp: bp.fitness)

    def evolution_history(self) -> list[EvolutionGeneration]:
        return list(self._generation_log)
