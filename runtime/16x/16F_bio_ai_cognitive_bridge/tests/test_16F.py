"""Tests for 16F Bio-AI Cognitive Bridge"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "16F"


def test_pulse_classification() -> None:
    from bio_cognitive import CognitivePulse, BrainwaveFreq
    gamma_pulse = CognitivePulse("p1", frequency_hz=40.0, amplitude=0.8)
    assert gamma_pulse.brainwave_type == BrainwaveFreq.GAMMA
    theta_pulse = CognitivePulse("p2", frequency_hz=6.0, amplitude=0.5)
    assert theta_pulse.brainwave_type == BrainwaveFreq.THETA


def test_state_analysis_dominant_wave() -> None:
    from bio_cognitive import BioCognitiveBridge, CognitivePulse
    bridge = BioCognitiveBridge()
    for i in range(20):
        bridge.ingest_pulse(CognitivePulse(f"p{i}", frequency_hz=40.0, amplitude=0.9))
    state = bridge.analyze_state()
    from bio_cognitive import BrainwaveFreq
    assert state.dominant_wave == BrainwaveFreq.GAMMA


def test_intent_translation() -> None:
    from bio_cognitive import BioCognitiveBridge, CognitivePulse, CognitiveState, BrainwaveFreq
    bridge = BioCognitiveBridge()
    state = CognitiveState("s1", BrainwaveFreq.THETA, coherence=0.8, cognitive_load=0.3)
    intent = bridge.translate_to_intent(state)
    assert intent == "creative_synthesis"


def test_bridge_stats() -> None:
    from bio_cognitive import BioCognitiveBridge, CognitivePulse
    bridge = BioCognitiveBridge()
    bridge.ingest_pulse(CognitivePulse("p1", 10.0, 0.5))
    bridge.ingest_pulse(CognitivePulse("p2", 25.0, 0.7))
    bridge.analyze_state()
    stats = bridge.bridge_stats()
    assert stats["buffer_size"] == 2
    assert stats["analyzed_states"] == 1
