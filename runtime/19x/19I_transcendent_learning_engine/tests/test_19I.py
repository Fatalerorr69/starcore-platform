"""Tests for 19I Transcendent Learning Engine"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "19I"


def test_supervised_perfect_match():
    from transcendent_learning import LearningEpisode, LearningParadigm
    ep = LearningEpisode("e1", LearningParadigm.SUPERVISED,
                         inputs=[1.0, 2.0], targets=[1.0, 2.0])
    loss = ep.compute_loss()
    assert loss == 0.0


def test_rl_full_reward_zero_loss():
    from transcendent_learning import LearningEpisode, LearningParadigm
    ep = LearningEpisode("e2", LearningParadigm.REINFORCEMENT,
                         inputs=[], reward=1.0)
    loss = ep.compute_loss()
    assert loss == 0.0


def test_learn_records_episode():
    from transcendent_learning import TranscendentLearner, LearningEpisode, LearningParadigm
    learner = TranscendentLearner()
    ep = LearningEpisode("e1", LearningParadigm.META, inputs=[0.5])
    learner.learn(ep)
    assert len(learner._episodes) == 1


def test_learner_stats_keys():
    from transcendent_learning import TranscendentLearner
    learner = TranscendentLearner()
    stats = learner.learner_stats()
    for key in ("episodes", "average_loss", "learning_rate", "paradigm_counts"):
        assert key in stats
