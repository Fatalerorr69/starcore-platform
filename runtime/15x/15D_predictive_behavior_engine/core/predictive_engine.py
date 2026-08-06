"""15D — Predictive Behavior Engine: Time-Series Predictor & Scenario Simulator"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import math
import time


@dataclass
class Observation:
    value: float
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Prediction:
    predicted_value: float
    confidence: float  # 0–1
    horizon_seconds: float
    method: str
    lower_bound: float = 0.0
    upper_bound: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Scenario:
    name: str
    description: str
    probability: float
    predicted_values: list[float] = field(default_factory=list)
    impact: str = "unknown"


class TimeSeriesPredictor:
    """Simple exponential smoothing + linear trend predictor."""

    def __init__(self, alpha: float = 0.3, beta: float = 0.1) -> None:
        self._alpha = alpha
        self._beta = beta
        self._observations: list[Observation] = []
        self._level: float | None = None
        self._trend: float = 0.0

    def observe(self, obs: Observation) -> None:
        self._observations.append(obs)
        if self._level is None:
            self._level = obs.value
        else:
            prev_level = self._level
            self._level = self._alpha * obs.value + (1 - self._alpha) * (prev_level + self._trend)
            self._trend = self._beta * (self._level - prev_level) + (1 - self._beta) * self._trend

    def predict(self, horizon_steps: int = 1) -> Prediction:
        if self._level is None:
            return Prediction(0.0, 0.0, float(horizon_steps), "none")
        predicted = self._level + horizon_steps * self._trend
        std = self._rolling_std()
        confidence = max(0.0, 1.0 - (std / (abs(predicted) + 1e-9)) * horizon_steps * 0.1)
        return Prediction(
            predicted_value=predicted,
            confidence=min(confidence, 0.99),
            horizon_seconds=float(horizon_steps),
            method="double_exponential_smoothing",
            lower_bound=predicted - 2 * std,
            upper_bound=predicted + 2 * std,
        )

    def _rolling_std(self, window: int = 20) -> float:
        recent = [o.value for o in self._observations[-window:]]
        if len(recent) < 2:
            return 0.0
        mean = sum(recent) / len(recent)
        return math.sqrt(sum((v - mean) ** 2 for v in recent) / len(recent))

    def is_anomaly(self, value: float, z_threshold: float = 3.0) -> bool:
        std = self._rolling_std()
        if self._level is None:
            return False
        if std < 1e-9:
            # Zero variance — any deviation > 10% of level is anomalous
            return abs(value - self._level) > max(abs(self._level) * 0.1, 0.01)
        return abs(value - self._level) > z_threshold * std


class ScenarioSimulator:
    """Generates multiple future scenarios from a predictor."""

    def __init__(self, predictor: TimeSeriesPredictor) -> None:
        self._predictor = predictor

    def simulate(self, horizon_steps: int = 10) -> list[Scenario]:
        base = self._predictor.predict(horizon_steps)
        std = self._predictor._rolling_std()
        return [
            Scenario(
                name="optimistic",
                description="Best-case trajectory",
                probability=0.25,
                predicted_values=[base.predicted_value + std * (i + 1) * 0.1
                                   for i in range(horizon_steps)],
                impact="positive",
            ),
            Scenario(
                name="baseline",
                description="Expected trajectory",
                probability=0.50,
                predicted_values=[
                    self._predictor.predict(i + 1).predicted_value
                    for i in range(horizon_steps)
                ],
                impact="neutral",
            ),
            Scenario(
                name="pessimistic",
                description="Worst-case trajectory",
                probability=0.25,
                predicted_values=[base.predicted_value - std * (i + 1) * 0.15
                                   for i in range(horizon_steps)],
                impact="negative",
            ),
        ]
