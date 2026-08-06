"""17A — Adaptive Neural Architecture: self-tuning layered network."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import math
import random


class ActivationType(str, Enum):
    RELU = "relu"
    SIGMOID = "sigmoid"
    TANH = "tanh"
    LINEAR = "linear"


def _activate(x: float, fn: ActivationType) -> float:
    if fn == ActivationType.RELU:
        return max(0.0, x)
    if fn == ActivationType.SIGMOID:
        return 1.0 / (1.0 + math.exp(-max(-500.0, min(500.0, x))))
    if fn == ActivationType.TANH:
        return math.tanh(x)
    return x


@dataclass
class NeuralLayer:
    layer_id: str
    input_size: int
    output_size: int
    activation: ActivationType = ActivationType.RELU
    weights: list[list[float]] = field(default_factory=list)
    biases: list[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.weights:
            scale = math.sqrt(2.0 / (self.input_size + self.output_size))
            self.weights = [
                [random.gauss(0, scale) for _ in range(self.output_size)]
                for _ in range(self.input_size)
            ]
        if not self.biases:
            self.biases = [0.0] * self.output_size

    def forward(self, inputs: list[float]) -> list[float]:
        return [
            _activate(
                self.biases[j] + sum(inputs[i] * self.weights[i][j]
                                     for i in range(min(len(inputs), self.input_size))),
                self.activation,
            )
            for j in range(self.output_size)
        ]


class AdaptiveNeuralNetwork:
    def __init__(self, learning_rate: float = 0.01) -> None:
        self._layers: list[NeuralLayer] = []
        self._lr = learning_rate
        self._performance_history: list[float] = []
        self._adaptations = 0

    def add_layer(self, layer: NeuralLayer) -> None:
        self._layers.append(layer)

    def forward(self, inputs: list[float]) -> list[float]:
        x = inputs
        for layer in self._layers:
            x = layer.forward(x)
        return x

    def record_performance(self, score: float) -> None:
        self._performance_history.append(score)

    def adapt(self) -> str:
        if len(self._performance_history) < 5:
            return "insufficient_data"
        recent = self._performance_history[-5:]
        trend = recent[-1] - recent[0]
        if trend < -0.05 and self._layers:
            last = self._layers[-1]
            for i in range(last.input_size):
                last.weights[i] = [w * 0.9 for w in last.weights[i]]
            self._adaptations += 1
            return "pruned"
        return "stable_improving" if trend > 0.05 else "no_change"

    def architecture_summary(self) -> dict[str, Any]:
        return {
            "layers": len(self._layers),
            "adaptations": self._adaptations,
            "layer_sizes": [(l.input_size, l.output_size) for l in self._layers],
            "avg_performance": (sum(self._performance_history) / len(self._performance_history)
                                if self._performance_history else 0.0),
        }
