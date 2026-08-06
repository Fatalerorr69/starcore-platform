"""15G — Neuromorphic Computing Interface: Spiking Neural Network & Hebbian Learning"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import math
import time


@dataclass
class Neuron:
    neuron_id: str
    threshold: float = 1.0
    membrane_potential: float = 0.0
    refractory_period: float = 0.005  # seconds
    last_spike_time: float = field(default=-1.0)
    spike_count: int = 0

    def receive(self, input_current: float, dt: float = 0.001) -> bool:
        """Leaky integrate-and-fire model. Returns True if neuron fires."""
        tau = 0.02  # membrane time constant
        leak = -self.membrane_potential / tau
        self.membrane_potential += (leak + input_current) * dt

        if self.membrane_potential >= self.threshold:
            self.membrane_potential = 0.0
            self.last_spike_time = time.time()
            self.spike_count += 1
            return True
        return False


@dataclass
class Synapse:
    pre_id: str
    post_id: str
    weight: float = 0.5
    delay: float = 0.001  # seconds
    plasticity: bool = True


class SpikingNetwork:
    """Spiking neural network with Hebbian plasticity."""

    def __init__(self, learning_rate: float = 0.01) -> None:
        self._neurons: dict[str, Neuron] = {}
        self._synapses: list[Synapse] = []
        self._lr = learning_rate
        self._spike_history: list[tuple[str, float]] = []

    def add_neuron(self, neuron: Neuron) -> None:
        self._neurons[neuron.neuron_id] = neuron

    def connect(self, synapse: Synapse) -> None:
        self._synapses.append(synapse)

    def step(self, inputs: dict[str, float], dt: float = 0.001) -> dict[str, bool]:
        spikes: dict[str, bool] = {}

        # Apply external inputs
        for nid, current in inputs.items():
            neuron = self._neurons.get(nid)
            if neuron:
                fired = neuron.receive(current, dt)
                spikes[nid] = fired
                if fired:
                    self._spike_history.append((nid, time.time()))

        # Propagate through synapses
        for syn in self._synapses:
            if spikes.get(syn.pre_id):
                post = self._neurons.get(syn.post_id)
                if post:
                    fired = post.receive(syn.weight, dt)
                    spikes[syn.post_id] = fired or spikes.get(syn.post_id, False)
                    if fired:
                        self._spike_history.append((syn.post_id, time.time()))

        # Hebbian plasticity: strengthen connections that co-fire
        if self._lr > 0:
            for syn in self._synapses:
                if syn.plasticity and spikes.get(syn.pre_id) and spikes.get(syn.post_id):
                    syn.weight = min(1.0, syn.weight + self._lr)

        return spikes

    def network_stats(self) -> dict[str, Any]:
        return {
            "neurons": len(self._neurons),
            "synapses": len(self._synapses),
            "total_spikes": sum(n.spike_count for n in self._neurons.values()),
            "recent_spikes": len(self._spike_history[-100:]),
        }

    def encode_rate(self, value: float, neuron_id: str, duration_steps: int = 100) -> int:
        """Rate coding: fire proportionally to input magnitude."""
        spikes = 0
        neuron = self._neurons.get(neuron_id)
        if not neuron:
            return 0
        scaled = value * neuron.threshold * 2
        for _ in range(duration_steps):
            if neuron.receive(scaled):
                spikes += 1
        return spikes
