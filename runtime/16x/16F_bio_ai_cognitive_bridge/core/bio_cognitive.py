"""16F — Bio-AI Cognitive Bridge: Brainwave-to-AI intent mapping."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import math
import time


class BrainwaveFreq(str, Enum):
    DELTA = "delta"
    THETA = "theta"
    ALPHA = "alpha"
    BETA = "beta"
    GAMMA = "gamma"


FREQ_RANGES: dict[BrainwaveFreq, tuple[float, float]] = {
    BrainwaveFreq.DELTA: (0.5, 4.0),
    BrainwaveFreq.THETA: (4.0, 8.0),
    BrainwaveFreq.ALPHA: (8.0, 13.0),
    BrainwaveFreq.BETA: (13.0, 30.0),
    BrainwaveFreq.GAMMA: (30.0, 100.0),
}


@dataclass
class CognitivePulse:
    pulse_id: str
    frequency_hz: float
    amplitude: float
    timestamp: float = field(default_factory=time.time)
    source: str = "synthetic"

    @property
    def brainwave_type(self) -> BrainwaveFreq:
        for bw, (lo, hi) in FREQ_RANGES.items():
            if lo <= self.frequency_hz < hi:
                return bw
        return BrainwaveFreq.GAMMA


@dataclass
class CognitiveState:
    state_id: str
    dominant_wave: BrainwaveFreq
    coherence: float
    cognitive_load: float
    timestamp: float = field(default_factory=time.time)


class BioCognitiveBridge:
    def __init__(self, buffer_size: int = 500) -> None:
        self._buffer: list[CognitivePulse] = []
        self._buffer_size = buffer_size
        self._states: list[CognitiveState] = []

    def ingest_pulse(self, pulse: CognitivePulse) -> None:
        self._buffer.append(pulse)
        if len(self._buffer) > self._buffer_size:
            self._buffer = self._buffer[-self._buffer_size:]

    def analyze_state(self, window: int = 50) -> CognitiveState:
        recent = self._buffer[-window:] if self._buffer else []
        if not recent:
            return CognitiveState("empty", BrainwaveFreq.ALPHA, 0.0, 0.0)
        wave_energy: dict[BrainwaveFreq, float] = {w: 0.0 for w in BrainwaveFreq}
        for pulse in recent:
            wave_energy[pulse.brainwave_type] += pulse.amplitude ** 2
        dominant = max(wave_energy, key=lambda w: wave_energy[w])
        amplitudes = [p.amplitude for p in recent]
        mean_amp = sum(amplitudes) / len(amplitudes)
        std_amp = math.sqrt(sum((a - mean_amp) ** 2 for a in amplitudes) / len(amplitudes))
        coherence = max(0.0, 1.0 - std_amp)
        high_freq = wave_energy[BrainwaveFreq.BETA] + wave_energy[BrainwaveFreq.GAMMA]
        total = sum(wave_energy.values())
        load = high_freq / (total + 1e-9)
        state = CognitiveState(
            state_id=f"state_{int(time.time() * 1000)}",
            dominant_wave=dominant,
            coherence=round(coherence, 4),
            cognitive_load=round(load, 4),
        )
        self._states.append(state)
        return state

    def translate_to_intent(self, state: CognitiveState) -> str:
        if state.dominant_wave == BrainwaveFreq.GAMMA and state.cognitive_load > 0.7:
            return "high_performance_task"
        if state.dominant_wave == BrainwaveFreq.THETA:
            return "creative_synthesis"
        if state.dominant_wave == BrainwaveFreq.ALPHA:
            return "reflective_analysis"
        if state.dominant_wave == BrainwaveFreq.DELTA:
            return "memory_consolidation"
        return "standard_processing"

    def bridge_stats(self) -> dict[str, Any]:
        return {"buffer_size": len(self._buffer), "analyzed_states": len(self._states)}
