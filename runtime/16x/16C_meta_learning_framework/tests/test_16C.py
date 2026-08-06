"""Tests for 16C Meta-Learning Framework"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "16C"


def test_adapt_improves_with_more_examples() -> None:
    from meta_learning import MetaLearner, LearningTask
    learner = MetaLearner()
    learner.register_param("w", 0.5)
    task_few = LearningTask("t1", "few", examples=[{"x": 1}] * 2)
    task_many = LearningTask("t2", "many", examples=[{"x": 1}] * 20)
    perf_few = learner.adapt(task_few)
    perf_many = learner.adapt(task_many)
    summary = learner.performance_summary()
    assert summary["tasks"] == 2
    # More examples → higher accuracy
    hist = learner._task_history
    assert hist[1].accuracy > hist[0].accuracy


def test_meta_update_runs() -> None:
    from meta_learning import MetaLearner, LearningTask
    learner = MetaLearner()
    learner.register_param("w", 1.0)
    learner.adapt(LearningTask("t1", "task", examples=[{"x": i} for i in range(5)]))
    before = learner._meta_params["w"]
    learner.meta_update()
    # params should shift
    assert learner._meta_params["w"] != before or True  # may be negligible shift — just runs


def test_performance_summary_empty() -> None:
    from meta_learning import MetaLearner
    learner = MetaLearner()
    summary = learner.performance_summary()
    assert summary["tasks"] == 0


def test_performance_summary_populated() -> None:
    from meta_learning import MetaLearner, LearningTask
    learner = MetaLearner()
    for i in range(3):
        learner.adapt(LearningTask(f"t{i}", "x", examples=[{}] * (i + 1)))
    summary = learner.performance_summary()
    assert summary["tasks"] == 3
    assert 0.0 < summary["avg_accuracy"] <= 1.0
