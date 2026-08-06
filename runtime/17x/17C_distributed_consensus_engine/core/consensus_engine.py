"""17C — Distributed Consensus Engine: BFT quorum-based consensus."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import hashlib
import time


class VoteType(str, Enum):
    COMMIT = "commit"
    ABORT = "abort"


class ConsensusState(str, Enum):
    PENDING = "pending"
    COMMITTED = "committed"
    ABORTED = "aborted"


@dataclass
class ConsensusNode:
    node_id: str
    is_faulty: bool = False


@dataclass
class ConsensusProposal:
    proposal_id: str
    value: Any
    proposer_id: str
    state: ConsensusState = ConsensusState.PENDING
    votes: dict[str, VoteType] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    @property
    def digest(self) -> str:
        return hashlib.sha256(str(self.value).encode()).hexdigest()[:12]


class ConsensusEngine:
    """BFT consensus: commit requires 2/3+1 honest votes."""

    def __init__(self) -> None:
        self._nodes: dict[str, ConsensusNode] = {}
        self._proposals: dict[str, ConsensusProposal] = {}

    def add_node(self, node: ConsensusNode) -> None:
        self._nodes[node.node_id] = node

    def propose(self, proposal: ConsensusProposal) -> str:
        self._proposals[proposal.proposal_id] = proposal
        return proposal.proposal_id

    def vote(self, node_id: str, proposal_id: str, vote: VoteType) -> None:
        node = self._nodes.get(node_id)
        proposal = self._proposals.get(proposal_id)
        if not node or not proposal or node.is_faulty:
            return
        proposal.votes[node_id] = vote

    def resolve(self, proposal_id: str) -> ConsensusState:
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return ConsensusState.ABORTED
        honest = [n for n in self._nodes.values() if not n.is_faulty]
        required = (len(honest) * 2) // 3 + 1
        commit_votes = sum(
            1 for nid, v in proposal.votes.items()
            if v == VoteType.COMMIT
            and nid in self._nodes and not self._nodes[nid].is_faulty
        )
        abort_votes = sum(
            1 for nid, v in proposal.votes.items()
            if v == VoteType.ABORT
            and nid in self._nodes and not self._nodes[nid].is_faulty
        )
        if commit_votes >= required:
            proposal.state = ConsensusState.COMMITTED
        elif abort_votes >= required:
            proposal.state = ConsensusState.ABORTED
        return proposal.state

    def consensus_health(self) -> dict[str, Any]:
        total = len(self._proposals)
        committed = sum(1 for p in self._proposals.values()
                        if p.state == ConsensusState.COMMITTED)
        return {
            "nodes": len(self._nodes),
            "faulty_nodes": sum(1 for n in self._nodes.values() if n.is_faulty),
            "proposals": total,
            "committed": committed,
            "commit_rate": round(committed / total, 4) if total else 0.0,
        }
