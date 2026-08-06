"""17B — Multi-Modal Fusion Engine: weighted late-fusion of heterogeneous signals."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time


class Modality(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    VISUAL = "visual"
    SENSOR = "sensor"
    TEMPORAL = "temporal"


@dataclass
class ModalSignal:
    signal_id: str
    modality: Modality
    features: list[float]
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FusedRepresentation:
    fusion_id: str
    combined_features: list[float]
    contributing_modalities: list[Modality]
    fusion_confidence: float
    timestamp: float = field(default_factory=time.time)


class MultiModalFusionEngine:
    def __init__(self, target_dim: int = 32) -> None:
        self._target_dim = target_dim
        self._signals: dict[Modality, list[ModalSignal]] = {m: [] for m in Modality}
        self._fusions: list[FusedRepresentation] = []

    def ingest(self, signal: ModalSignal) -> None:
        self._signals[signal.modality].append(signal)

    def _project(self, features: list[float]) -> list[float]:
        n = self._target_dim
        if len(features) >= n:
            return features[:n]
        return features + [0.0] * (n - len(features))

    def fuse(self, modalities: list[Modality] | None = None) -> FusedRepresentation:
        mods = modalities if modalities is not None else list(Modality)
        selected = [self._signals[m][-1] for m in mods if self._signals[m]]
        if not selected:
            return FusedRepresentation(
                fusion_id="empty",
                combined_features=[0.0] * self._target_dim,
                contributing_modalities=[],
                fusion_confidence=0.0,
            )
        total_w = sum(s.confidence for s in selected)
        combined = [0.0] * self._target_dim
        for sig in selected:
            proj = self._project(sig.features)
            w = sig.confidence / total_w
            for i in range(self._target_dim):
                combined[i] += proj[i] * w
        fusion = FusedRepresentation(
            fusion_id=f"f{int(time.time()*1000)}",
            combined_features=combined,
            contributing_modalities=[s.modality for s in selected],
            fusion_confidence=min(1.0, total_w / len(selected)),
        )
        self._fusions.append(fusion)
        return fusion

    def fusion_stats(self) -> dict[str, Any]:
        return {
            "total_fusions": len(self._fusions),
            "active_modalities": sum(1 for m in Modality if self._signals[m]),
        }
