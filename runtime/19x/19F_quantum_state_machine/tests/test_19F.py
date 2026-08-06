"""Tests for 19F Quantum State Machine"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "19F"


def test_state_probability():
    from quantum_state_machine import QState
    s = QState("s0", amplitude=complex(1.0, 0.0))
    assert s.probability == 1.0


def test_initialize_full_probability():
    from quantum_state_machine import QuantumStateMachine, QState
    qsm = QuantumStateMachine()
    qsm.add_state(QState("s0"))
    qsm.initialize("s0")
    assert qsm._current["s0"] == 1.0


def test_step_transitions_probability():
    from quantum_state_machine import QuantumStateMachine, QState, QTransition
    qsm = QuantumStateMachine()
    qsm.add_state(QState("A"))
    qsm.add_state(QState("B"))
    qsm.add_transition(QTransition("A", "B", probability=1.0))
    qsm.initialize("A")
    dist = qsm.step()
    assert "B" in dist
    assert abs(dist["B"] - 1.0) < 1e-9


def test_measure_returns_dominant():
    from quantum_state_machine import QuantumStateMachine, QState, QTransition
    qsm = QuantumStateMachine()
    qsm.add_state(QState("X"))
    qsm.add_state(QState("Y"))
    qsm.add_transition(QTransition("X", "Y", probability=0.8))
    qsm.add_transition(QTransition("X", "X", probability=0.2))
    qsm.initialize("X")
    qsm.step()
    dominant = qsm.measure()
    assert dominant == "Y"
