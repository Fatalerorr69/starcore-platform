"""18B — Neuroplastic Adaptation Engine: Hebbian synaptic weight adaptation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import math


@dataclass
class SynapticConnection:
    source: str
    target: str
    weight: float = 0.5
    plasticity: float = 1.0

    def strengthen(self, amount: float) -> None:
        self.weight = min(1.0, self.weight + amount * self.plasticity)

    def weaken(self, amount: float) -> None:
        self.weight = max(0.0, self.weight - amount * self.plasticity)

    def adapt(self, signal: float) -> None:
        if signal > 0:
            self.strengthen(abs(signal) * 0.1)
        else:
            self.weaken(abs(signal) * 0.1)


@dataclass
class NeuroplasticLayer:
    layer_id: str
    neurons: int = 10
    connections: list[SynapticConnection] = field(default_factory=list)
    activation_history: list[float] = field(default_factory=list)

    def add_connection(self, conn: SynapticConnection) -> None:
        self.connections.append(conn)

    def activate(self, inputs: list[float]) -> list[float]:
        result = [math.tanh(v) for v in inputs[:self.neurons]]
        self.activation_history.append(sum(result) / max(1, len(result)))
        return result

    def prune(self, threshold: float = 0.1) -> int:
        before = len(self.connections)
        self.connections = [c for c in self.connections if c.weight >= threshold]
        return before - len(self.connections)


class NeuroplasticBrain:
    def __init__(self, learning_rate: float = 0.01) -> None:
        self._lr = learning_rate
        self._layers: list[NeuroplasticLayer] = []
        self._adaptations: int = 0

    def add_layer(self, layer: NeuroplasticLayer) -> None:
        self._layers.append(layer)

    def adapt(self, feedback: float) -> None:
        for layer in self._layers:
            for conn in layer.connections:
                conn.adapt(feedback * self._lr)
        self._adaptations += 1

    def stats(self) -> dict[str, Any]:
        total_conn = sum(len(l.connections) for l in self._layers)
        return {
            "layers": len(self._layers),
            "total_connections": total_conn,
            "adaptations": self._adaptations,
        }
