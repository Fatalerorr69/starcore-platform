"""Datové modely pro Prompt Registry, Session Ledger a QC Engines."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any


class PromptType(StrEnum):
    MASTER = "MASTER"
    AUDIT = "AUDIT"
    IMPLEMENTATION = "IMPLEMENTATION"
    RECOVERY = "RECOVERY"
    UTILITY = "UTILITY"


class PromptStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DRAFT = "DRAFT"
    SUPERSEDED = "SUPERSEDED"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"
    REJECTED = "REJECTED"


class PromptSource(StrEnum):
    USER = "USER"
    AGENT = "AGENT"
    EXTERNAL = "EXTERNAL"


@dataclass
class PromptEntry:
    id: str
    name: str
    version: str
    type: PromptType
    purpose: str
    status: PromptStatus
    source: PromptSource
    created_at: str
    updated_at: str
    phase: str | None = None
    supersedes: str | None = None
    superseded_by: str | None = None
    dependencies: list[str] = field(default_factory=list)
    session_id: str | None = None
    tags: list[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "type": str(self.type),
            "purpose": self.purpose,
            "phase": self.phase,
            "status": str(self.status),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "source": str(self.source),
            "supersedes": self.supersedes,
            "superseded_by": self.superseded_by,
            "dependencies": self.dependencies,
            "session_id": self.session_id,
            "tags": self.tags,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PromptEntry:
        return cls(
            id=data["id"],
            name=data["name"],
            version=data.get("version", "1.0"),
            type=PromptType(data.get("type", "UTILITY")),
            purpose=data.get("purpose", ""),
            status=PromptStatus(data.get("status", "ACTIVE")),
            source=PromptSource(data.get("source", "USER")),
            created_at=data.get("created_at", str(date.today())),
            updated_at=data.get("updated_at", str(date.today())),
            phase=data.get("phase"),
            supersedes=data.get("supersedes"),
            superseded_by=data.get("superseded_by"),
            dependencies=data.get("dependencies", []),
            session_id=data.get("session_id"),
            tags=data.get("tags", []),
            description=data.get("description", ""),
        )


@dataclass
class TestRun:
    timestamp: str
    passed: int
    failed: int
    coverage: float
    command: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "passed": self.passed,
            "failed": self.failed,
            "coverage": self.coverage,
            "command": self.command,
        }


@dataclass
class SessionEntry:
    session_id: str
    start_time: str
    branch: str
    head: str
    end_time: str | None = None
    user_requests: list[str] = field(default_factory=list)
    prompts_used: list[str] = field(default_factory=list)
    files_read: list[str] = field(default_factory=list)
    files_created: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    commands_executed: list[str] = field(default_factory=list)
    tests_executed: list[dict[str, Any]] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    approvals: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    next_action: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "branch": self.branch,
            "head": self.head,
            "user_requests": self.user_requests,
            "prompts_used": self.prompts_used,
            "files_read": self.files_read,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "commands_executed": self.commands_executed,
            "tests_executed": self.tests_executed,
            "decisions": self.decisions,
            "risks": self.risks,
            "approvals": self.approvals,
            "blockers": self.blockers,
            "next_action": self.next_action,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionEntry:
        return cls(
            session_id=data["session_id"],
            start_time=data["start_time"],
            branch=data["branch"],
            head=data["head"],
            end_time=data.get("end_time"),
            user_requests=data.get("user_requests", []),
            prompts_used=data.get("prompts_used", []),
            files_read=data.get("files_read", []),
            files_created=data.get("files_created", []),
            files_modified=data.get("files_modified", []),
            commands_executed=data.get("commands_executed", []),
            tests_executed=data.get("tests_executed", []),
            decisions=data.get("decisions", []),
            risks=data.get("risks", []),
            approvals=data.get("approvals", []),
            blockers=data.get("blockers", []),
            next_action=data.get("next_action", ""),
        )

    def is_active(self) -> bool:
        return self.end_time is None


def now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── QC Engine models ──────────────────────────────────────────────────────────


class CheckState(StrEnum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


_ICONS: dict[str, str] = {
    "PASS": "✓",
    "WARNING": "⚠",
    "FAIL": "✗",
    "UNKNOWN": "?",
    "NOT_APPLICABLE": "—",
}

# Priority order for rolling up multiple results (highest wins)
_STATE_PRIORITY: dict[str, int] = {
    "FAIL": 4,
    "UNKNOWN": 3,
    "WARNING": 2,
    "PASS": 1,
    "NOT_APPLICABLE": 0,
}


@dataclass
class CheckResult:
    name: str
    state: CheckState
    detail: str
    evidence: list[str] = field(default_factory=list)

    @property
    def icon(self) -> str:
        return _ICONS.get(str(self.state), "?")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "state": str(self.state),
            "detail": self.detail,
            "evidence": self.evidence,
        }


def worst_state(results: list[CheckResult]) -> CheckState:
    """Return the highest-priority state from a list of results."""
    if not results:
        return CheckState.UNKNOWN
    worst = max(results, key=lambda r: _STATE_PRIORITY.get(str(r.state), 0))
    return worst.state
