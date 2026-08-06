"""9F — Digital Twin Runtime"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import time
import copy


@dataclass
class TwinState:
    entity_id: str
    properties: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    version: int = 0


class DigitalTwin:
    def __init__(self, entity_id: str) -> None:
        self.entity_id = entity_id
        self._real_state: TwinState = TwinState(entity_id=entity_id)
        self._simulated_state: TwinState = TwinState(entity_id=entity_id)
        self._history: list[TwinState] = []

    def update_real(self, properties: dict[str, Any]) -> None:
        self._history.append(copy.deepcopy(self._real_state))
        self._real_state.properties.update(properties)
        self._real_state.timestamp = time.time()
        self._real_state.version += 1

    def simulate(self, delta: dict[str, Any]) -> TwinState:
        simulated = copy.deepcopy(self._real_state)
        simulated.properties.update(delta)
        simulated.timestamp = time.time()
        self._simulated_state = simulated
        return simulated

    def divergence(self) -> dict[str, Any]:
        diffs: dict[str, Any] = {}
        for key in set(self._real_state.properties) | set(self._simulated_state.properties):
            r = self._real_state.properties.get(key)
            s = self._simulated_state.properties.get(key)
            if r != s:
                diffs[key] = {"real": r, "simulated": s}
        return diffs

    def sync(self) -> None:
        self._real_state = copy.deepcopy(self._simulated_state)
        self._real_state.timestamp = time.time()
