"""Tests for 17C Distributed Consensus Engine"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17C"


def test_proposal_creation():
    from consensus_engine import ConsensusEngine, ConsensusNode, ConsensusProposal
    eng = ConsensusEngine()
    eng.add_node(ConsensusNode("n1"))
    pid = eng.propose(ConsensusProposal("p1", "value_x", "n1"))
    assert pid == "p1"


def test_commits_with_quorum():
    from consensus_engine import ConsensusEngine, ConsensusNode, ConsensusProposal, VoteType, ConsensusState
    eng = ConsensusEngine()
    for i in range(4):
        eng.add_node(ConsensusNode(f"n{i}"))
    eng.propose(ConsensusProposal("p1", "data", "n0"))
    for i in range(3):  # 3/4 = 75% > 66%
        eng.vote(f"n{i}", "p1", VoteType.COMMIT)
    assert eng.resolve("p1") == ConsensusState.COMMITTED


def test_faulty_nodes_excluded():
    from consensus_engine import ConsensusEngine, ConsensusNode, ConsensusProposal, VoteType, ConsensusState
    eng = ConsensusEngine()
    eng.add_node(ConsensusNode("honest1"))
    eng.add_node(ConsensusNode("honest2"))
    eng.add_node(ConsensusNode("faulty", is_faulty=True))
    eng.propose(ConsensusProposal("p1", "val", "honest1"))
    eng.vote("faulty", "p1", VoteType.COMMIT)   # faulty vote ignored
    eng.vote("honest1", "p1", VoteType.COMMIT)
    eng.vote("honest2", "p1", VoteType.COMMIT)
    assert eng.resolve("p1") == ConsensusState.COMMITTED


def test_no_commit_without_quorum():
    from consensus_engine import ConsensusEngine, ConsensusNode, ConsensusProposal, VoteType, ConsensusState
    eng = ConsensusEngine()
    for i in range(4):
        eng.add_node(ConsensusNode(f"n{i}"))
    eng.propose(ConsensusProposal("p1", "data", "n0"))
    eng.vote("n0", "p1", VoteType.COMMIT)  # only 1/4 = 25% < 66%
    state = eng.resolve("p1")
    assert state == ConsensusState.PENDING
