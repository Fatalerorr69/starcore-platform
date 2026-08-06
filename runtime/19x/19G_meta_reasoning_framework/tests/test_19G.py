"""Tests for 19G Meta-Reasoning Framework"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "19G"


def test_deductive_with_3_premises():
    from meta_reasoning import ReasoningTrace, ReasoningStrategy
    trace = ReasoningTrace("t1", ReasoningStrategy.DEDUCTIVE,
                           premises=["p1", "p2", "p3"], conclusion="C")
    conf = trace.evaluate()
    assert abs(conf - 0.9) < 1e-9  # base=0.9, 3/3=1.0


def test_best_strategy_is_deductive():
    from meta_reasoning import MetaReasoningFramework, ReasoningStrategy
    fw = MetaReasoningFramework()
    assert fw.best_strategy() == ReasoningStrategy.DEDUCTIVE


def test_reason_adds_trace():
    from meta_reasoning import MetaReasoningFramework, ReasoningTrace, ReasoningStrategy
    fw = MetaReasoningFramework()
    trace = ReasoningTrace("t1", ReasoningStrategy.INDUCTIVE,
                           premises=["a", "b", "c"])
    fw.reason(trace)
    assert len(fw._traces) == 1


def test_framework_stats():
    from meta_reasoning import MetaReasoningFramework, ReasoningTrace, ReasoningStrategy
    fw = MetaReasoningFramework()
    fw.reason(ReasoningTrace("t1", ReasoningStrategy.ABDUCTIVE,
                             premises=["x", "y", "z"]))
    stats = fw.framework_stats()
    assert "traces" in stats
    assert "meta_confidence" in stats
    assert stats["traces"] == 1
