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
