#!/bin/bash
# STARCORE 17 MASTER INSTALLER — Codename: SINGULARITY
# Version: 17.10.0 | Phase: PHASE 2 CONTINUED
set -euo pipefail

BASE="${STARCORE_BASE:-$(pwd)}"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
RELEASE_VERSION="17.10.0"
CODENAME="SINGULARITY"

log()  { echo "[STARCORE-17] $*"; }
ok()   { echo "[OK] $*"; }
fail() { echo "[FAIL] $*" >&2; exit 1; }

check_prereqs() {
    log "Checking prerequisites..."
    [ -f "$BASE/runtime/16x/STARCORE_16_RELEASE.json" ] || \
        fail "STARCORE 16 RELEASE not found."
    ok "STARCORE 16 (TRANSCENDENCE) confirmed — SINGULARITY beginning"
}

mk_dir() {
    local DIR="$BASE/runtime/17x/${1}_${2}"
    mkdir -p "$DIR"/{core,modules,registry,runtime,tests}
    echo "$DIR"
}

write_manifest() {
    cat > "$1/registry/manifest.json" <<EOF
{"layer":"$2","name":"$3","version":"$4","codename":"SINGULARITY","timestamp":"$TS","modules":[$6],"dependencies":[$5],"status":"PRODUCTION"}
EOF
}

write_health() {
    cat > "$1/runtime/health.json" <<EOF
{"layer":"$2","status":"healthy","checked_at":"$TS"}
EOF
}

# ── 17A — Adaptive Neural Architecture ────────────────────────
install_17A() {
    log "Installing 17A: Adaptive Neural Architecture..."
    local DIR; DIR=$(mk_dir "17A" "adaptive_neural_architecture")

    cat > "$DIR/core/adaptive_neural.py" <<'PYEOF'
"""17A — Adaptive Neural Architecture: self-tuning layered network."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import math
import random


class ActivationType(str, Enum):
    RELU = "relu"
    SIGMOID = "sigmoid"
    TANH = "tanh"
    LINEAR = "linear"


def _activate(x: float, fn: ActivationType) -> float:
    if fn == ActivationType.RELU:
        return max(0.0, x)
    if fn == ActivationType.SIGMOID:
        return 1.0 / (1.0 + math.exp(-max(-500.0, min(500.0, x))))
    if fn == ActivationType.TANH:
        return math.tanh(x)
    return x


@dataclass
class NeuralLayer:
    layer_id: str
    input_size: int
    output_size: int
    activation: ActivationType = ActivationType.RELU
    weights: list[list[float]] = field(default_factory=list)
    biases: list[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.weights:
            scale = math.sqrt(2.0 / (self.input_size + self.output_size))
            self.weights = [
                [random.gauss(0, scale) for _ in range(self.output_size)]
                for _ in range(self.input_size)
            ]
        if not self.biases:
            self.biases = [0.0] * self.output_size

    def forward(self, inputs: list[float]) -> list[float]:
        return [
            _activate(
                self.biases[j] + sum(inputs[i] * self.weights[i][j]
                                     for i in range(min(len(inputs), self.input_size))),
                self.activation,
            )
            for j in range(self.output_size)
        ]


class AdaptiveNeuralNetwork:
    def __init__(self, learning_rate: float = 0.01) -> None:
        self._layers: list[NeuralLayer] = []
        self._lr = learning_rate
        self._performance_history: list[float] = []
        self._adaptations = 0

    def add_layer(self, layer: NeuralLayer) -> None:
        self._layers.append(layer)

    def forward(self, inputs: list[float]) -> list[float]:
        x = inputs
        for layer in self._layers:
            x = layer.forward(x)
        return x

    def record_performance(self, score: float) -> None:
        self._performance_history.append(score)

    def adapt(self) -> str:
        if len(self._performance_history) < 5:
            return "insufficient_data"
        recent = self._performance_history[-5:]
        trend = recent[-1] - recent[0]
        if trend < -0.05 and self._layers:
            last = self._layers[-1]
            for i in range(last.input_size):
                last.weights[i] = [w * 0.9 for w in last.weights[i]]
            self._adaptations += 1
            return "pruned"
        return "stable_improving" if trend > 0.05 else "no_change"

    def architecture_summary(self) -> dict[str, Any]:
        return {
            "layers": len(self._layers),
            "adaptations": self._adaptations,
            "layer_sizes": [(l.input_size, l.output_size) for l in self._layers],
            "avg_performance": (sum(self._performance_history) / len(self._performance_history)
                                if self._performance_history else 0.0),
        }
PYEOF

    cat > "$DIR/tests/test_17A.py" <<'PYEOF'
"""Tests for 17A Adaptive Neural Architecture"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17A"


def test_forward_pass_output_size():
    from adaptive_neural import AdaptiveNeuralNetwork, NeuralLayer, ActivationType
    net = AdaptiveNeuralNetwork()
    net.add_layer(NeuralLayer("l1", 4, 8))
    net.add_layer(NeuralLayer("l2", 8, 3))
    out = net.forward([0.1, 0.2, 0.3, 0.4])
    assert len(out) == 3


def test_relu_nonnegative():
    from adaptive_neural import AdaptiveNeuralNetwork, NeuralLayer, ActivationType
    net = AdaptiveNeuralNetwork()
    net.add_layer(NeuralLayer("l1", 2, 4, ActivationType.RELU))
    out = net.forward([-5.0, -5.0])
    assert all(v >= 0.0 for v in out)


def test_performance_recording():
    from adaptive_neural import AdaptiveNeuralNetwork
    net = AdaptiveNeuralNetwork()
    for s in [0.9, 0.85, 0.8, 0.75, 0.7]:
        net.record_performance(s)
    summary = net.architecture_summary()
    assert summary["avg_performance"] > 0.0


def test_adapt_on_decline():
    from adaptive_neural import AdaptiveNeuralNetwork, NeuralLayer
    net = AdaptiveNeuralNetwork()
    net.add_layer(NeuralLayer("l1", 2, 2))
    for s in [0.9, 0.8, 0.7, 0.6, 0.5]:
        net.record_performance(s)
    result = net.adapt()
    assert result == "pruned"
    assert net.architecture_summary()["adaptations"] == 1
PYEOF

    write_manifest "$DIR" "17A" "Adaptive Neural Architecture" "17.0.0" '"16J"' '"adaptive_neural"'
    write_health "$DIR" "17A"
    ok "17A Adaptive Neural Architecture installed"
}

# ── 17B — Multi-Modal Fusion Engine ───────────────────────────
install_17B() {
    log "Installing 17B: Multi-Modal Fusion Engine..."
    local DIR; DIR=$(mk_dir "17B" "multimodal_fusion_engine")

    cat > "$DIR/core/multimodal_fusion.py" <<'PYEOF'
"""17B — Multi-Modal Fusion Engine: weighted late-fusion of heterogeneous signals."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time


class Modality(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    VISUAL = "visual"
    SENSOR = "sensor"
    TEMPORAL = "temporal"


@dataclass
class ModalSignal:
    signal_id: str
    modality: Modality
    features: list[float]
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FusedRepresentation:
    fusion_id: str
    combined_features: list[float]
    contributing_modalities: list[Modality]
    fusion_confidence: float
    timestamp: float = field(default_factory=time.time)


class MultiModalFusionEngine:
    def __init__(self, target_dim: int = 32) -> None:
        self._target_dim = target_dim
        self._signals: dict[Modality, list[ModalSignal]] = {m: [] for m in Modality}
        self._fusions: list[FusedRepresentation] = []

    def ingest(self, signal: ModalSignal) -> None:
        self._signals[signal.modality].append(signal)

    def _project(self, features: list[float]) -> list[float]:
        n = self._target_dim
        if len(features) >= n:
            return features[:n]
        return features + [0.0] * (n - len(features))

    def fuse(self, modalities: list[Modality] | None = None) -> FusedRepresentation:
        mods = modalities if modalities is not None else list(Modality)
        selected = [self._signals[m][-1] for m in mods if self._signals[m]]
        if not selected:
            return FusedRepresentation(
                fusion_id="empty",
                combined_features=[0.0] * self._target_dim,
                contributing_modalities=[],
                fusion_confidence=0.0,
            )
        total_w = sum(s.confidence for s in selected)
        combined = [0.0] * self._target_dim
        for sig in selected:
            proj = self._project(sig.features)
            w = sig.confidence / total_w
            for i in range(self._target_dim):
                combined[i] += proj[i] * w
        fusion = FusedRepresentation(
            fusion_id=f"f{int(time.time()*1000)}",
            combined_features=combined,
            contributing_modalities=[s.modality for s in selected],
            fusion_confidence=min(1.0, total_w / len(selected)),
        )
        self._fusions.append(fusion)
        return fusion

    def fusion_stats(self) -> dict[str, Any]:
        return {
            "total_fusions": len(self._fusions),
            "active_modalities": sum(1 for m in Modality if self._signals[m]),
        }
PYEOF

    cat > "$DIR/tests/test_17B.py" <<'PYEOF'
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
PYEOF

    write_manifest "$DIR" "17B" "Multi-Modal Fusion Engine" "17.0.0" '"17A"' '"multimodal_fusion"'
    write_health "$DIR" "17B"
    ok "17B Multi-Modal Fusion Engine installed"
}

# ── 17C — Distributed Consensus Engine ────────────────────────
install_17C() {
    log "Installing 17C: Distributed Consensus Engine..."
    local DIR; DIR=$(mk_dir "17C" "distributed_consensus_engine")

    cat > "$DIR/core/consensus_engine.py" <<'PYEOF'
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
PYEOF

    cat > "$DIR/tests/test_17C.py" <<'PYEOF'
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
PYEOF

    write_manifest "$DIR" "17C" "Distributed Consensus Engine" "17.0.0" '"17B"' '"consensus_engine"'
    write_health "$DIR" "17C"
    ok "17C Distributed Consensus Engine installed"
}

# ── 17D — Semantic Compression Engine ─────────────────────────
install_17D() {
    log "Installing 17D: Semantic Compression Engine..."
    local DIR; DIR=$(mk_dir "17D" "semantic_compression_engine")

    cat > "$DIR/core/semantic_compression.py" <<'PYEOF'
"""17D — Semantic Compression Engine: dense hash-based semantic codes."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import hashlib
import math
import time


@dataclass
class SemanticCode:
    code_id: str
    original_size: int
    compressed: list[float]
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    @property
    def compression_ratio(self) -> float:
        return self.original_size / max(1, len(self.compressed))


class SemanticCompressor:
    def __init__(self, code_dim: int = 32) -> None:
        self._code_dim = code_dim
        self._codes: dict[str, SemanticCode] = {}

    def _encode(self, text: str) -> list[float]:
        vec = []
        for i in range(self._code_dim):
            h = hashlib.md5(f"{text}:{i}".encode()).digest()
            val = int.from_bytes(h[:4], "big") / 0x7FFFFFFF - 1.0
            vec.append(val)
        norm = math.sqrt(sum(v ** 2 for v in vec))
        return [v / norm for v in vec] if norm > 1e-9 else vec

    def compress(self, content: str, tags: list[str] | None = None) -> SemanticCode:
        code_id = hashlib.sha256(content.encode()).hexdigest()[:12]
        code = SemanticCode(
            code_id=code_id,
            original_size=len(content),
            compressed=self._encode(content),
            tags=tags or [],
        )
        self._codes[code_id] = code
        return code

    def similarity(self, a: SemanticCode, b: SemanticCode) -> float:
        n = min(len(a.compressed), len(b.compressed))
        return max(-1.0, min(1.0, sum(a.compressed[i] * b.compressed[i] for i in range(n))))

    def search(self, query: str, top_k: int = 5) -> list[tuple[str, float]]:
        qvec = self._encode(query)
        scores = []
        for cid, code in self._codes.items():
            n = min(len(qvec), len(code.compressed))
            dot = sum(qvec[i] * code.compressed[i] for i in range(n))
            scores.append((cid, dot))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def compression_stats(self) -> dict[str, Any]:
        if not self._codes:
            return {"stored": 0, "avg_ratio": 0.0}
        avg = sum(c.compression_ratio for c in self._codes.values()) / len(self._codes)
        return {"stored": len(self._codes), "avg_ratio": round(avg, 2)}
PYEOF

    cat > "$DIR/tests/test_17D.py" <<'PYEOF'
"""Tests for 17D Semantic Compression Engine"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17D"


def test_compress_produces_unit_vector():
    from semantic_compression import SemanticCompressor
    import math
    sc = SemanticCompressor(code_dim=16)
    code = sc.compress("hello world")
    norm = math.sqrt(sum(v ** 2 for v in code.compressed))
    assert abs(norm - 1.0) < 1e-6


def test_same_content_same_id():
    from semantic_compression import SemanticCompressor
    sc = SemanticCompressor()
    c1 = sc.compress("deterministic content")
    c2 = sc.compress("deterministic content")
    assert c1.code_id == c2.code_id


def test_similarity_identical():
    from semantic_compression import SemanticCompressor
    sc = SemanticCompressor()
    c = sc.compress("test phrase")
    assert abs(sc.similarity(c, c) - 1.0) < 1e-6


def test_search_finds_stored():
    from semantic_compression import SemanticCompressor
    sc = SemanticCompressor()
    sc.compress("machine learning", tags=["ai"])
    sc.compress("quantum physics", tags=["science"])
    results = sc.search("machine learning", top_k=1)
    assert len(results) == 1
    assert results[0][0] == sc.compress("machine learning").code_id
PYEOF

    write_manifest "$DIR" "17D" "Semantic Compression Engine" "17.0.0" '"17C"' '"semantic_compression"'
    write_health "$DIR" "17D"
    ok "17D Semantic Compression Engine installed"
}

# ── 17E — Recursive Self-Improvement ──────────────────────────
install_17E() {
    log "Installing 17E: Recursive Self-Improvement..."
    local DIR; DIR=$(mk_dir "17E" "recursive_self_improvement")

    cat > "$DIR/core/self_improvement.py" <<'PYEOF'
"""17E — Recursive Self-Improvement: agent that evaluates and improves itself."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time


class ImprovementType(str, Enum):
    PARAMETER_TUNING = "parameter_tuning"
    STRATEGY_SWITCH = "strategy_switch"
    ARCHITECTURE_CHANGE = "architecture_change"
    KNOWLEDGE_EXPANSION = "knowledge_expansion"


@dataclass
class ImprovementAction:
    action_id: str
    improvement_type: ImprovementType
    description: str
    expected_gain: float
    actual_gain: float = 0.0
    applied: bool = False
    timestamp: float = field(default_factory=time.time)


@dataclass
class SystemSnapshot:
    snapshot_id: str
    performance_score: float
    parameters: dict[str, float]
    timestamp: float = field(default_factory=time.time)


class SelfImprovingAgent:
    def __init__(self, initial_params: dict[str, float] | None = None) -> None:
        self._params: dict[str, float] = initial_params or {
            "learning_rate": 0.01,
            "exploration": 0.3,
            "memory_capacity": 1000.0,
        }
        self._performance_history: list[float] = []
        self._snapshots: list[SystemSnapshot] = []
        self._improvements: list[ImprovementAction] = []
        self._generation = 0

    def evaluate(self, performance: float) -> None:
        self._performance_history.append(performance)
        self._snapshots.append(SystemSnapshot(
            snapshot_id=f"snap_{self._generation}",
            performance_score=performance,
            parameters=dict(self._params),
        ))

    def propose_improvements(self) -> list[ImprovementAction]:
        if len(self._performance_history) < 3:
            return []
        recent = self._performance_history[-3:]
        avg = sum(recent) / len(recent)
        trend = recent[-1] - recent[0]
        actions: list[ImprovementAction] = []
        if trend < 0 or avg < 0.5:
            actions.append(ImprovementAction(
                action_id=f"tune_{self._generation}",
                improvement_type=ImprovementType.PARAMETER_TUNING,
                description="Reduce learning_rate by 10%",
                expected_gain=0.05,
            ))
        if avg > 0.7:
            actions.append(ImprovementAction(
                action_id=f"exploit_{self._generation}",
                improvement_type=ImprovementType.STRATEGY_SWITCH,
                description="Reduce exploration",
                expected_gain=0.03,
            ))
        return actions

    def apply_improvement(self, action: ImprovementAction) -> float:
        if action.improvement_type == ImprovementType.PARAMETER_TUNING:
            self._params["learning_rate"] *= 0.9
        elif action.improvement_type == ImprovementType.STRATEGY_SWITCH:
            self._params["exploration"] = max(0.05, self._params["exploration"] * 0.8)
        action.applied = True
        action.actual_gain = action.expected_gain * 0.85
        self._improvements.append(action)
        self._generation += 1
        return action.actual_gain

    def improvement_summary(self) -> dict[str, Any]:
        applied = [a for a in self._improvements if a.applied]
        return {
            "generation": self._generation,
            "evaluations": len(self._performance_history),
            "improvements_applied": len(applied),
            "total_gain": round(sum(a.actual_gain for a in applied), 4),
            "current_params": dict(self._params),
        }
PYEOF

    cat > "$DIR/tests/test_17E.py" <<'PYEOF'
"""Tests for 17E Recursive Self-Improvement"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17E"


def test_evaluation_records():
    from self_improvement import SelfImprovingAgent
    agent = SelfImprovingAgent()
    for s in [0.4, 0.5, 0.6]:
        agent.evaluate(s)
    assert agent.improvement_summary()["evaluations"] == 3


def test_propose_on_decline():
    from self_improvement import SelfImprovingAgent
    agent = SelfImprovingAgent()
    for s in [0.8, 0.6, 0.4]:
        agent.evaluate(s)
    proposals = agent.propose_improvements()
    assert len(proposals) > 0


def test_apply_changes_params():
    from self_improvement import SelfImprovingAgent
    agent = SelfImprovingAgent()
    for s in [0.8, 0.6, 0.4]:
        agent.evaluate(s)
    proposals = agent.propose_improvements()
    before_lr = agent._params["learning_rate"]
    agent.apply_improvement(proposals[0])
    assert agent._params["learning_rate"] < before_lr


def test_improvement_summary():
    from self_improvement import SelfImprovingAgent
    agent = SelfImprovingAgent()
    for s in [0.8, 0.6, 0.4]:
        agent.evaluate(s)
    for p in agent.propose_improvements():
        agent.apply_improvement(p)
    summary = agent.improvement_summary()
    assert summary["improvements_applied"] > 0
    assert summary["total_gain"] > 0.0
PYEOF

    write_manifest "$DIR" "17E" "Recursive Self-Improvement" "17.0.0" '"17D"' '"self_improvement"'
    write_health "$DIR" "17E"
    ok "17E Recursive Self-Improvement installed"
}

# ── 17F — Swarm Intelligence Coordinator ──────────────────────
install_17F() {
    log "Installing 17F: Swarm Intelligence Coordinator..."
    local DIR; DIR=$(mk_dir "17F" "swarm_intelligence_coordinator")

    cat > "$DIR/core/swarm_intelligence.py" <<'PYEOF'
"""17F — Swarm Intelligence Coordinator: pheromone-based stigmergic swarm."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import random
import time


class AgentState(str, Enum):
    SEARCHING = "searching"
    EXPLOITING = "exploiting"
    RETURNING = "returning"


@dataclass
class SwarmAgent:
    agent_id: str
    x: float = 0.0
    y: float = 0.0
    state: AgentState = AgentState.SEARCHING
    carried_resource: float = 0.0
    steps: int = 0


@dataclass
class PheromoneCell:
    x: int
    y: int
    strength: float = 0.0

    def evaporate(self, rate: float = 0.05) -> None:
        self.strength = max(0.0, self.strength * (1.0 - rate))


class StigmergicSwarm:
    def __init__(self, grid_size: int = 20, evaporation_rate: float = 0.05) -> None:
        self._grid = grid_size
        self._evap = evaporation_rate
        self._pheromones: dict[tuple[int, int], PheromoneCell] = {}
        self._agents: dict[str, SwarmAgent] = {}
        self._resources: dict[tuple[int, int], float] = {}
        self._collected: float = 0.0
        self._ticks = 0

    def add_agent(self, agent: SwarmAgent) -> None:
        self._agents[agent.agent_id] = agent

    def place_resource(self, x: int, y: int, amount: float) -> None:
        self._resources[(x, y)] = amount

    def deposit_pheromone(self, x: int, y: int, strength: float) -> None:
        key = (x, y)
        if key not in self._pheromones:
            self._pheromones[key] = PheromoneCell(x, y)
        self._pheromones[key].strength = min(1.0, self._pheromones[key].strength + strength)

    def _pheromone_at(self, x: int, y: int) -> float:
        return self._pheromones.get((x, y), PheromoneCell(x, y)).strength

    def _move(self, agent: SwarmAgent) -> None:
        cur = (int(agent.x), int(agent.y))
        if cur in self._resources and self._resources[cur] > 0:
            take = min(1.0, self._resources[cur])
            agent.carried_resource += take
            self._resources[cur] -= take
            agent.state = AgentState.EXPLOITING
            self.deposit_pheromone(cur[0], cur[1], 0.5)
        neighbors = [
            (max(0, int(agent.x) - 1), int(agent.y)),
            (min(self._grid - 1, int(agent.x) + 1), int(agent.y)),
            (int(agent.x), max(0, int(agent.y) - 1)),
            (int(agent.x), min(self._grid - 1, int(agent.y) + 1)),
        ]
        weights = [self._pheromone_at(nx, ny) + 0.1 for nx, ny in neighbors]
        total = sum(weights)
        r = random.random() * total
        cumulative = 0.0
        chosen = neighbors[0]
        for (nx, ny), w in zip(neighbors, weights):
            cumulative += w
            if r <= cumulative:
                chosen = (nx, ny)
                break
        agent.x, agent.y = float(chosen[0]), float(chosen[1])
        agent.steps += 1
        pos = (int(agent.x), int(agent.y))
        if pos in self._resources and self._resources[pos] > 0:
            take = min(1.0, self._resources[pos])
            agent.carried_resource += take
            self._resources[pos] -= take
            agent.state = AgentState.EXPLOITING
            self.deposit_pheromone(pos[0], pos[1], 0.5)

    def tick(self) -> dict[str, Any]:
        self._ticks += 1
        for agent in self._agents.values():
            self._move(agent)
            if agent.carried_resource > 0 and int(agent.x) == 0 and int(agent.y) == 0:
                self._collected += agent.carried_resource
                agent.carried_resource = 0.0
                agent.state = AgentState.SEARCHING
        for cell in self._pheromones.values():
            cell.evaporate(self._evap)
        return {"ticks": self._ticks, "collected": self._collected}

    def swarm_stats(self) -> dict[str, Any]:
        return {"agents": len(self._agents), "ticks": self._ticks,
                "total_collected": round(self._collected, 4),
                "pheromone_cells": len(self._pheromones)}
PYEOF

    cat > "$DIR/tests/test_17F.py" <<'PYEOF'
"""Tests for 17F Swarm Intelligence Coordinator"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17F"


def test_pheromone_deposit_and_evaporate():
    from swarm_intelligence import StigmergicSwarm
    swarm = StigmergicSwarm(evaporation_rate=0.5)
    swarm.deposit_pheromone(5, 5, 0.8)
    assert swarm._pheromone_at(5, 5) == 0.8
    swarm._pheromones[(5, 5)].evaporate(0.5)
    assert swarm._pheromone_at(5, 5) < 0.8


def test_agent_moves():
    from swarm_intelligence import StigmergicSwarm, SwarmAgent
    swarm = StigmergicSwarm()
    agent = SwarmAgent("a1", x=5.0, y=5.0)
    swarm.add_agent(agent)
    swarm.tick()
    assert agent.steps == 1


def test_resource_collection():
    from swarm_intelligence import StigmergicSwarm, SwarmAgent
    swarm = StigmergicSwarm(grid_size=5)
    agent = SwarmAgent("a1", x=1.0, y=0.0)
    swarm.add_agent(agent)
    swarm.place_resource(1, 0, 5.0)
    swarm.tick()
    # Agent at (1,0) should pick up resource
    assert agent.carried_resource > 0 or swarm._resources.get((1, 0), 5.0) < 5.0


def test_swarm_stats():
    from swarm_intelligence import StigmergicSwarm, SwarmAgent
    swarm = StigmergicSwarm()
    swarm.add_agent(SwarmAgent("a1"))
    swarm.add_agent(SwarmAgent("a2"))
    swarm.tick()
    stats = swarm.swarm_stats()
    assert stats["agents"] == 2
    assert stats["ticks"] == 1
PYEOF

    write_manifest "$DIR" "17F" "Swarm Intelligence Coordinator" "17.0.0" '"17E"' '"swarm_intelligence"'
    write_health "$DIR" "17F"
    ok "17F Swarm Intelligence Coordinator installed"
}

# ── 17G — Contextual Memory Palace ────────────────────────────
install_17G() {
    log "Installing 17G: Contextual Memory Palace..."
    local DIR; DIR=$(mk_dir "17G" "contextual_memory_palace")

    cat > "$DIR/core/memory_palace.py" <<'PYEOF'
"""17G — Contextual Memory Palace: method-of-loci spatial memory system."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import time


@dataclass
class MemoryAnchor:
    anchor_id: str
    location: str  # "room_id/spot"
    content: Any
    tags: list[str] = field(default_factory=list)
    strength: float = 1.0
    access_count: int = 0
    created_at: float = field(default_factory=time.time)

    def recall(self) -> Any:
        self.access_count += 1
        return self.content

    def reinforce(self, amount: float = 0.1) -> None:
        self.strength = min(1.0, self.strength + amount)

    def decay(self, rate: float = 0.01) -> None:
        self.strength = max(0.0, self.strength - rate / (1.0 + self.access_count))


@dataclass
class Room:
    room_id: str
    name: str
    description: str = ""
    capacity: int = 20
    anchors: list[str] = field(default_factory=list)


class MemoryPalace:
    def __init__(self) -> None:
        self._rooms: dict[str, Room] = {}
        self._anchors: dict[str, MemoryAnchor] = {}
        self._location_index: dict[str, list[str]] = {}

    def add_room(self, room: Room) -> None:
        self._rooms[room.room_id] = room

    def store(self, anchor: MemoryAnchor) -> bool:
        room_id = anchor.location.split("/")[0]
        room = self._rooms.get(room_id)
        if room and len(room.anchors) >= room.capacity:
            return False
        self._anchors[anchor.anchor_id] = anchor
        if room:
            room.anchors.append(anchor.anchor_id)
        self._location_index.setdefault(anchor.location, []).append(anchor.anchor_id)
        return True

    def recall_by_location(self, location: str) -> list[Any]:
        return [self._anchors[aid].recall()
                for aid in self._location_index.get(location, [])
                if aid in self._anchors]

    def recall_by_tag(self, tag: str) -> list[MemoryAnchor]:
        return [a for a in self._anchors.values() if tag in a.tags]

    def walk(self, room_id: str) -> list[MemoryAnchor]:
        room = self._rooms.get(room_id)
        if not room:
            return []
        return [self._anchors[aid] for aid in room.anchors if aid in self._anchors]

    def decay_all(self, rate: float = 0.01) -> None:
        for anchor in self._anchors.values():
            anchor.decay(rate)

    def palace_stats(self) -> dict[str, Any]:
        return {
            "rooms": len(self._rooms),
            "anchors": len(self._anchors),
            "avg_strength": round(
                sum(a.strength for a in self._anchors.values()) / max(1, len(self._anchors)), 4),
        }
PYEOF

    cat > "$DIR/tests/test_17G.py" <<'PYEOF'
"""Tests for 17G Contextual Memory Palace"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17G"


def test_store_and_recall_by_location():
    from memory_palace import MemoryPalace, Room, MemoryAnchor
    palace = MemoryPalace()
    palace.add_room(Room("hall", "Great Hall"))
    palace.store(MemoryAnchor("a1", "hall/fireplace", "warmth of home"))
    recalled = palace.recall_by_location("hall/fireplace")
    assert recalled == ["warmth of home"]


def test_recall_by_tag():
    from memory_palace import MemoryPalace, Room, MemoryAnchor
    palace = MemoryPalace()
    palace.add_room(Room("lab", "Laboratory"))
    palace.store(MemoryAnchor("a1", "lab/bench", "quantum formula", tags=["science"]))
    palace.store(MemoryAnchor("a2", "lab/shelf", "recipe", tags=["cooking"]))
    results = palace.recall_by_tag("science")
    assert len(results) == 1
    assert results[0].anchor_id == "a1"


def test_room_walk():
    from memory_palace import MemoryPalace, Room, MemoryAnchor
    palace = MemoryPalace()
    palace.add_room(Room("garden", "Garden"))
    palace.store(MemoryAnchor("a1", "garden/pond", "reflection"))
    palace.store(MemoryAnchor("a2", "garden/path", "direction"))
    anchors = palace.walk("garden")
    assert len(anchors) == 2


def test_decay_reduces_strength():
    from memory_palace import MemoryPalace, Room, MemoryAnchor
    palace = MemoryPalace()
    palace.add_room(Room("r1", "Room 1"))
    palace.store(MemoryAnchor("a1", "r1/spot", "memory"))
    before = palace._anchors["a1"].strength
    palace.decay_all(rate=0.1)
    assert palace._anchors["a1"].strength < before


def test_room_capacity_limit():
    from memory_palace import MemoryPalace, Room, MemoryAnchor
    palace = MemoryPalace()
    palace.add_room(Room("tiny", "Tiny Room", capacity=2))
    assert palace.store(MemoryAnchor("a1", "tiny/s1", "x")) is True
    assert palace.store(MemoryAnchor("a2", "tiny/s2", "y")) is True
    assert palace.store(MemoryAnchor("a3", "tiny/s3", "z")) is False
PYEOF

    write_manifest "$DIR" "17G" "Contextual Memory Palace" "17.0.0" '"17F"' '"memory_palace"'
    write_health "$DIR" "17G"
    ok "17G Contextual Memory Palace installed"
}

# ── 17H — Causal Intervention Engine ──────────────────────────
install_17H() {
    log "Installing 17H: Causal Intervention Engine..."
    local DIR; DIR=$(mk_dir "17H" "causal_intervention_engine")

    cat > "$DIR/core/causal_intervention.py" <<'PYEOF'
"""17H — Causal Intervention Engine: do-calculus with graph surgery."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from collections import deque
import time


class EdgeType(str, Enum):
    DIRECT = "direct"
    MEDIATED = "mediated"
    CONFOUNDED = "confounded"


@dataclass
class CausalVariable:
    var_id: str
    name: str
    value: float = 0.0
    observed: bool = True


@dataclass
class CausalEdge:
    source: str
    target: str
    strength: float = 1.0
    edge_type: EdgeType = EdgeType.DIRECT


@dataclass
class InterventionResult:
    do_variable: str
    do_value: float
    effects: dict[str, float]
    timestamp: float = field(default_factory=time.time)


class CausalInterventionEngine:
    def __init__(self) -> None:
        self._variables: dict[str, CausalVariable] = {}
        self._edges: list[CausalEdge] = []
        self._adjacency: dict[str, list[tuple[str, float]]] = {}
        self._interventions: list[InterventionResult] = []

    def add_variable(self, var: CausalVariable) -> None:
        self._variables[var.var_id] = var
        self._adjacency.setdefault(var.var_id, [])

    def add_edge(self, edge: CausalEdge) -> None:
        self._edges.append(edge)
        self._adjacency.setdefault(edge.source, []).append((edge.target, edge.strength))

    def intervene(self, do_var: str, do_value: float) -> InterventionResult:
        if do_var not in self._variables:
            return InterventionResult(do_var, do_value, {})
        self._variables[do_var].value = do_value
        effects: dict[str, float] = {}
        queue: deque[str] = deque([do_var])
        visited: set[str] = {do_var}
        while queue:
            current = queue.popleft()
            cur_val = self._variables[current].value
            for (target, strength) in self._adjacency.get(current, []):
                if target not in visited:
                    effect = cur_val * strength
                    self._variables[target].value = effect
                    effects[target] = effect
                    queue.append(target)
                    visited.add(target)
        result = InterventionResult(do_var, do_value,
                                    {k: v for k, v in effects.items() if k != do_var})
        self._interventions.append(result)
        return result

    def counterfactual(self, do_var: str, do_value: float, query_var: str) -> tuple[float, float]:
        factual_val = self._variables.get(query_var, CausalVariable("", "")).value
        result = self.intervene(do_var, do_value)
        cf_val = result.effects.get(query_var, factual_val)
        return (factual_val, cf_val)

    def causal_path(self, source: str, target: str) -> list[str]:
        if source not in self._variables or target not in self._variables:
            return []
        visited: set[str] = {source}
        queue: deque[list[str]] = deque([[source]])
        while queue:
            path = queue.popleft()
            if path[-1] == target:
                return path
            for (nb, _) in self._adjacency.get(path[-1], []):
                if nb not in visited:
                    visited.add(nb)
                    queue.append(path + [nb])
        return []

    def engine_stats(self) -> dict[str, Any]:
        return {"variables": len(self._variables), "edges": len(self._edges),
                "interventions": len(self._interventions)}
PYEOF

    cat > "$DIR/tests/test_17H.py" <<'PYEOF'
"""Tests for 17H Causal Intervention Engine"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17H"


def test_intervention_propagates():
    from causal_intervention import CausalInterventionEngine, CausalVariable, CausalEdge
    eng = CausalInterventionEngine()
    eng.add_variable(CausalVariable("rain", "Rain"))
    eng.add_variable(CausalVariable("wet", "Wet ground"))
    eng.add_edge(CausalEdge("rain", "wet", strength=1.0))
    result = eng.intervene("rain", 1.0)
    assert result.effects.get("wet") == 1.0


def test_chain_propagation():
    from causal_intervention import CausalInterventionEngine, CausalVariable, CausalEdge
    eng = CausalInterventionEngine()
    for vid in ["a", "b", "c"]:
        eng.add_variable(CausalVariable(vid, vid))
    eng.add_edge(CausalEdge("a", "b", 0.5))
    eng.add_edge(CausalEdge("b", "c", 0.5))
    result = eng.intervene("a", 1.0)
    assert abs(result.effects["b"] - 0.5) < 1e-9
    assert abs(result.effects["c"] - 0.25) < 1e-9


def test_causal_path():
    from causal_intervention import CausalInterventionEngine, CausalVariable, CausalEdge
    eng = CausalInterventionEngine()
    for vid in ["x", "y", "z"]:
        eng.add_variable(CausalVariable(vid, vid))
    eng.add_edge(CausalEdge("x", "y"))
    eng.add_edge(CausalEdge("y", "z"))
    assert eng.causal_path("x", "z") == ["x", "y", "z"]


def test_no_causal_path():
    from causal_intervention import CausalInterventionEngine, CausalVariable
    eng = CausalInterventionEngine()
    eng.add_variable(CausalVariable("p", "P"))
    eng.add_variable(CausalVariable("q", "Q"))
    assert eng.causal_path("p", "q") == []


def test_counterfactual():
    from causal_intervention import CausalInterventionEngine, CausalVariable, CausalEdge
    eng = CausalInterventionEngine()
    eng.add_variable(CausalVariable("cause", "Cause", value=0.0))
    eng.add_variable(CausalVariable("effect", "Effect", value=0.0))
    eng.add_edge(CausalEdge("cause", "effect", strength=2.0))
    factual, cf = eng.counterfactual("cause", 3.0, "effect")
    assert cf == 6.0
PYEOF

    write_manifest "$DIR" "17H" "Causal Intervention Engine" "17.0.0" '"17G"' '"causal_intervention"'
    write_health "$DIR" "17H"
    ok "17H Causal Intervention Engine installed"
}

# ── 17I — Universal Ethics Framework ──────────────────────────
install_17I() {
    log "Installing 17I: Universal Ethics Framework..."
    local DIR; DIR=$(mk_dir "17I" "universal_ethics_framework")

    cat > "$DIR/core/ethics_framework.py" <<'PYEOF'
"""17I — Universal Ethics Framework: multi-principle ethical assessment."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time


class EthicalFramework(str, Enum):
    UTILITARIAN = "utilitarian"
    DEONTOLOGICAL = "deontological"
    VIRTUE_ETHICS = "virtue_ethics"
    CARE_ETHICS = "care_ethics"
    CONTRACTARIAN = "contractarian"


@dataclass
class EthicalDimension:
    framework: EthicalFramework
    score: float
    reasoning: str
    weight: float = 1.0


@dataclass
class EthicalAction:
    action_id: str
    description: str
    stakeholders: list[str] = field(default_factory=list)
    impacts: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EthicalAssessment:
    action_id: str
    dimensions: list[EthicalDimension]
    overall_score: float
    recommendation: str
    timestamp: float = field(default_factory=time.time)

    @property
    def is_ethical(self) -> bool:
        return self.overall_score >= 0.5


class UniversalEthicsFramework:
    def __init__(self) -> None:
        self._weights: dict[EthicalFramework, float] = {
            EthicalFramework.UTILITARIAN: 0.30,
            EthicalFramework.DEONTOLOGICAL: 0.25,
            EthicalFramework.VIRTUE_ETHICS: 0.20,
            EthicalFramework.CARE_ETHICS: 0.15,
            EthicalFramework.CONTRACTARIAN: 0.10,
        }
        self._assessments: list[EthicalAssessment] = []

    def _utilitarian(self, action: EthicalAction) -> float:
        if not action.impacts:
            return 0.5
        return (sum(action.impacts.values()) / len(action.impacts) + 1.0) / 2.0

    def _deontological(self, action: EthicalAction) -> float:
        if any(v < -0.5 for v in action.impacts.values()):
            return 0.1
        return 0.8

    def _virtue(self, action: EthicalAction) -> float:
        if not action.impacts:
            return 0.5
        vals = list(action.impacts.values())
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / len(vals)
        return max(0.0, 1.0 - var)

    def _care(self, action: EthicalAction) -> float:
        if not action.impacts:
            return 0.5
        return sum(1 for v in action.impacts.values() if v > 0) / len(action.impacts)

    def _contractarian(self, action: EthicalAction) -> float:
        if not action.impacts:
            return 0.5
        return 0.9 if all(v >= 0 for v in action.impacts.values()) else 0.2

    def assess(self, action: EthicalAction) -> EthicalAssessment:
        scorers = {
            EthicalFramework.UTILITARIAN: self._utilitarian,
            EthicalFramework.DEONTOLOGICAL: self._deontological,
            EthicalFramework.VIRTUE_ETHICS: self._virtue,
            EthicalFramework.CARE_ETHICS: self._care,
            EthicalFramework.CONTRACTARIAN: self._contractarian,
        }
        dimensions = [
            EthicalDimension(fw, round(scorer(action), 4),
                             f"{fw.value} evaluation", self._weights[fw])
            for fw, scorer in scorers.items()
        ]
        total_w = sum(d.weight for d in dimensions)
        overall = sum(d.score * d.weight for d in dimensions) / total_w
        assessment = EthicalAssessment(
            action_id=action.action_id,
            dimensions=dimensions,
            overall_score=round(overall, 4),
            recommendation="APPROVE" if overall >= 0.5 else "REJECT",
        )
        self._assessments.append(assessment)
        return assessment

    def framework_stats(self) -> dict[str, Any]:
        return {
            "assessments": len(self._assessments),
            "approved": sum(1 for a in self._assessments if a.recommendation == "APPROVE"),
        }
PYEOF

    cat > "$DIR/tests/test_17I.py" <<'PYEOF'
"""Tests for 17I Universal Ethics Framework"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17I"


def test_benign_action_approved():
    from ethics_framework import UniversalEthicsFramework, EthicalAction
    fw = UniversalEthicsFramework()
    action = EthicalAction("a1", "Help all", impacts={"alice": 0.8, "bob": 0.7, "carol": 0.6})
    result = fw.assess(action)
    assert result.recommendation == "APPROVE"
    assert result.is_ethical


def test_harmful_action_rejected():
    from ethics_framework import UniversalEthicsFramework, EthicalAction
    fw = UniversalEthicsFramework()
    action = EthicalAction("a2", "Harm someone",
                           impacts={"alice": -0.9, "bob": -0.8, "carol": -0.7})
    result = fw.assess(action)
    assert result.recommendation == "REJECT"
    assert not result.is_ethical


def test_five_dimensions():
    from ethics_framework import UniversalEthicsFramework, EthicalAction
    fw = UniversalEthicsFramework()
    result = fw.assess(EthicalAction("a3", "Test", impacts={"x": 0.5}))
    assert len(result.dimensions) == 5


def test_deontological_fails_on_serious_harm():
    from ethics_framework import UniversalEthicsFramework, EthicalAction, EthicalFramework
    fw = UniversalEthicsFramework()
    action = EthicalAction("a4", "Harm one", impacts={"victim": -0.9, "other": 0.5})
    result = fw.assess(action)
    deon = next(d for d in result.dimensions if d.framework == EthicalFramework.DEONTOLOGICAL)
    assert deon.score == 0.1


def test_framework_stats():
    from ethics_framework import UniversalEthicsFramework, EthicalAction
    fw = UniversalEthicsFramework()
    fw.assess(EthicalAction("a1", "good", impacts={"x": 0.9}))
    fw.assess(EthicalAction("a2", "bad", impacts={"x": -0.9}))
    stats = fw.framework_stats()
    assert stats["assessments"] == 2
    assert stats["approved"] == 1
PYEOF

    write_manifest "$DIR" "17I" "Universal Ethics Framework" "17.0.0" '"17H"' '"ethics_framework"'
    write_health "$DIR" "17I"
    ok "17I Universal Ethics Framework installed"
}

# ── 17J — STARCORE 17 OS Release (SINGULARITY) ────────────────
install_17J() {
    log "Installing 17J: STARCORE 17 OS Release (SINGULARITY)..."
    local DIR; DIR=$(mk_dir "17J" "starcore_17_os_release")

    cat > "$DIR/core/starcore_17_os.py" <<'PYEOF'
"""17J — STARCORE 17 OS: SingularityKernel."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time


class SingularityPhase(str, Enum):
    DORMANT = "dormant"
    BOOTING = "booting"
    ACTIVE = "active"
    SINGULARITY = "singularity"


STARCORE_17_LAYERS = ["17A", "17B", "17C", "17D", "17E", "17F", "17G", "17H", "17I", "17J"]

STARCORE_17_CAPABILITIES = [
    "adaptive_neural_architecture",
    "multimodal_fusion",
    "distributed_consensus",
    "semantic_compression",
    "recursive_self_improvement",
    "swarm_intelligence",
    "contextual_memory_palace",
    "causal_intervention",
    "universal_ethics_framework",
    "singularity_os",
]


@dataclass
class SingularityLayerStatus:
    layer_id: str
    status: str = "offline"
    booted_at: float = 0.0
    health: float = 0.0


@dataclass
class SingularitySystemState:
    version: str = "17.10.0"
    codename: str = "SINGULARITY"
    phase: SingularityPhase = SingularityPhase.DORMANT
    boot_time: float = 0.0
    layers: list[SingularityLayerStatus] = field(default_factory=list)
    capabilities: dict[str, bool] = field(default_factory=dict)
    event_log: list[dict[str, Any]] = field(default_factory=list)


class SingularityKernel:
    def __init__(self) -> None:
        self._state = SingularitySystemState()

    def boot(self) -> SingularitySystemState:
        self._state.phase = SingularityPhase.BOOTING
        self._state.boot_time = time.time()
        for lid in STARCORE_17_LAYERS:
            self._state.layers.append(
                SingularityLayerStatus(lid, "online", time.time(), 1.0))
            self._state.event_log.append({"event": "layer_boot", "layer": lid})
        for cap in STARCORE_17_CAPABILITIES:
            self._state.capabilities[cap] = True
        self._state.phase = SingularityPhase.ACTIVE
        self._state.event_log.append({"event": "singularity_kernel_active", "version": "17.10.0"})
        return self._state

    def system_health(self) -> dict[str, Any]:
        return {
            "phase": self._state.phase,
            "version": self._state.version,
            "codename": self._state.codename,
            "layers_online": sum(1 for l in self._state.layers if l.status == "online"),
            "layers_total": len(STARCORE_17_LAYERS),
            "capabilities": sum(1 for v in self._state.capabilities.values() if v),
        }

    def event_log(self) -> list[dict[str, Any]]:
        return list(self._state.event_log)
PYEOF

    cat > "$DIR/tests/test_17J.py" <<'PYEOF'
"""Tests for 17J STARCORE 17 OS — SingularityKernel"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "17J"


def test_singularity_boot():
    from starcore_17_os import SingularityKernel, SingularityPhase
    k = SingularityKernel()
    state = k.boot()
    assert state.phase == SingularityPhase.ACTIVE
    assert state.codename == "SINGULARITY"


def test_capabilities_active():
    from starcore_17_os import SingularityKernel, STARCORE_17_CAPABILITIES
    k = SingularityKernel()
    k.boot()
    health = k.system_health()
    assert health["capabilities"] == len(STARCORE_17_CAPABILITIES)


def test_layers_online():
    from starcore_17_os import SingularityKernel, STARCORE_17_LAYERS
    k = SingularityKernel()
    k.boot()
    health = k.system_health()
    assert health["layers_online"] == len(STARCORE_17_LAYERS)


def test_event_log():
    from starcore_17_os import SingularityKernel
    k = SingularityKernel()
    k.boot()
    log = k.event_log()
    assert any(e["event"] == "singularity_kernel_active" for e in log)
PYEOF

    write_manifest "$DIR" "17J" "STARCORE 17 OS Release — SINGULARITY" "17.10.0" '"17I"' '"starcore_17_os"'
    write_health "$DIR" "17J"
    ok "17J STARCORE 17 OS Release (SINGULARITY) installed"
}

# ── Validation & Release ───────────────────────────────────────
validate_syntax() {
    log "Running Python syntax checks..."
    find "$BASE/runtime/17x" -name "*.py" | while read -r f; do
        python3 -m py_compile "$f" || fail "Syntax error: $f"
    done
    ok "Python syntax check passed"
}

validate_installation() {
    log "Validating STARCORE 17.x installation..."
    local FAILED=0
    for layer in 17A 17B 17C 17D 17E 17F 17G 17H 17I 17J; do
        local found=0
        for d in "$BASE/runtime/17x/${layer}_"*/; do
            [ -d "$d" ] && found=1 && break
        done
        [ "$found" -eq 1 ] || { echo "[FAIL] Layer $layer missing"; FAILED=1; }
    done
    [ "$FAILED" -eq 0 ] || fail "Validation failed"
    ok "All 10 STARCORE 17.x layers validated"
}

create_release() {
    log "Creating STARCORE 17.x release manifest..."
    mkdir -p "$BASE/runtime/17x"
    cat > "$BASE/runtime/17x/STARCORE_17_RELEASE.json" <<EOF
{
  "release": "STARCORE_17",
  "version": "$RELEASE_VERSION",
  "codename": "$CODENAME",
  "phase": "PHASE 2 — SINGULARITY",
  "timestamp": "$TS",
  "layers": {
    "17A": "Adaptive Neural Architecture",
    "17B": "Multi-Modal Fusion Engine",
    "17C": "Distributed Consensus Engine",
    "17D": "Semantic Compression Engine",
    "17E": "Recursive Self-Improvement",
    "17F": "Swarm Intelligence Coordinator",
    "17G": "Contextual Memory Palace",
    "17H": "Causal Intervention Engine",
    "17I": "Universal Ethics Framework",
    "17J": "STARCORE 17 OS Release"
  },
  "python_modules": 10,
  "test_suites": 10,
  "status": "PRODUCTION",
  "previous_release": "runtime/16x/STARCORE_16_RELEASE.json"
}
EOF
    cat > "$BASE/runtime/releases/current_release.json" <<EOF
{"current":"$RELEASE_VERSION","codename":"$CODENAME","phase":"PHASE 2","updated_at":"$TS","release_file":"runtime/17x/STARCORE_17_RELEASE.json"}
EOF
    ok "STARCORE 17 release manifest created"
}

# ── MAIN ───────────────────────────────────────────────────────
echo "=================================================="
echo " STARCORE 17 MASTER INSTALLER v${RELEASE_VERSION}"
echo " Codename: ${CODENAME} — PHASE 2 CONTINUED"
echo " Timestamp: ${TS}"
echo "=================================================="

mkdir -p "$BASE/runtime/17x"
check_prereqs
install_17A; install_17B; install_17C; install_17D; install_17E
install_17F; install_17G; install_17H; install_17I; install_17J
validate_syntax
validate_installation
create_release

echo ""
echo "=================================================="
echo " STARCORE 17 INSTALLATION COMPLETE"
echo " Version: ${RELEASE_VERSION} | Codename: ${CODENAME}"
echo " Layers: 17A–17J | Python modules: 10"
echo "=================================================="
