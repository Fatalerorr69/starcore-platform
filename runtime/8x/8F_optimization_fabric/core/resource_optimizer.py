"""8F — Optimization Fabric: Resource Optimizer"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResourceMetrics:
    cpu_percent: float
    memory_percent: float
    io_wait: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationAction:
    target: str
    action: str
    parameters: dict[str, Any] = field(default_factory=dict)
    priority: int = 5


class ResourceOptimizer:
    def __init__(self, cpu_threshold: float = 80.0, mem_threshold: float = 85.0) -> None:
        self._cpu_threshold = cpu_threshold
        self._mem_threshold = mem_threshold
        self._history: list[ResourceMetrics] = []

    def ingest(self, metrics: ResourceMetrics) -> None:
        self._history.append(metrics)
        if len(self._history) > 1000:
            self._history = self._history[-500:]

    def recommend(self, current: ResourceMetrics) -> list[OptimizationAction]:
        actions: list[OptimizationAction] = []
        if current.cpu_percent > self._cpu_threshold:
            actions.append(OptimizationAction(
                target="compute", action="scale_out",
                parameters={"reason": f"cpu={current.cpu_percent:.1f}%"}, priority=1
            ))
        if current.memory_percent > self._mem_threshold:
            actions.append(OptimizationAction(
                target="memory", action="evict_cache",
                parameters={"reason": f"mem={current.memory_percent:.1f}%"}, priority=2
            ))
        return actions
