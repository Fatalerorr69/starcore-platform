"""Tests for 17B Multi-Modal Fusion Engine"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17B"


def test_ingest_and_fuse():
    from multimodal_fusion import MultiModalFusionEngine, ModalSignal, Modality
    engine = MultiModalFusionEngine(target_dim=4)
    engine.ingest(ModalSignal("s1", Modality.TEXT, [1.0, 0.0, 0.0, 0.0]))
    engine.ingest(ModalSignal("s2", Modality.AUDIO, [0.0, 1.0, 0.0, 0.0]))
    result = engine.fuse([Modality.TEXT, Modality.AUDIO])
    assert len(result.combined_features) == 4
    assert len(result.contributing_modalities) == 2


def test_empty_fusion():
    from multimodal_fusion import MultiModalFusionEngine, Modality
    engine = MultiModalFusionEngine(target_dim=4)
    result = engine.fuse([Modality.VISUAL])
    assert result.fusion_confidence == 0.0


def test_confidence_weights_fusion():
    from multimodal_fusion import MultiModalFusionEngine, ModalSignal, Modality
    engine = MultiModalFusionEngine(target_dim=2)
    engine.ingest(ModalSignal("s1", Modality.TEXT, [1.0, 0.0], confidence=0.9))
    engine.ingest(ModalSignal("s2", Modality.AUDIO, [0.0, 1.0], confidence=0.1))
    result = engine.fuse([Modality.TEXT, Modality.AUDIO])
    # TEXT has 9x weight, so first feature should dominate
    assert result.combined_features[0] > result.combined_features[1]
