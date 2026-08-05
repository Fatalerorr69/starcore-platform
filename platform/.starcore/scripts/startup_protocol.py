#!/usr/bin/env python3
"""
STARCORE Autonomous Operating System — Startup Protocol.

Implements the 12-step startup flow. Call at the beginning of every new
session to produce a Czech session status report with a decision menu.

Použití:
  uv run python .starcore/scripts/startup_protocol.py
  uv run python .starcore/scripts/startup_protocol.py --quick
  uv run python .starcore/scripts/startup_protocol.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

_SCRIPT_DIR = Path(__file__).parent
_STARCORE_DIR = _SCRIPT_DIR.parent
_REPO_ROOT = _STARCORE_DIR.parent

sys.path.insert(0, str(_SCRIPT_DIR))
from models import CheckState, SessionEntry  # noqa: E402

_SEP = "═" * 72
_SEP2 = "─" * 72


# ── Data structures ───────────────────────────────────────────────────────────


@dataclass
class GitInfo:
    repo: str
    remote: str
    branch: str
    head: str
    head_msg: str
    worktree_clean: bool
    worktree_summary: str


@dataclass
class RiskEntry:
    id: str
    title: str
    severity: str
    status: str


@dataclass
class StartupState:
    git: GitInfo
    last_session: SessionEntry | None
    open_risks: list[RiskEntry]
    p1_items: list[str]
    recent_decisions: list[str]
    sentinel_state: CheckState
    sentinel_detail: str
    release_verdict: str
    release_blockers: list[str]
    quick: bool = False

    def to_dict(self) -> dict:
        return {
            "git": asdict(self.git),
            "last_session": (self.last_session.to_dict() if self.last_session else None),
            "open_risks": [asdict(r) for r in self.open_risks],
            "p1_items": self.p1_items,
            "recent_decisions": self.recent_decisions,
            "sentinel_state": str(self.sentinel_state),
            "sentinel_detail": self.sentinel_detail,
            "release_verdict": self.release_verdict,
            "release_blockers": self.release_blockers,
            "quick": self.quick,
        }


# ── Step 1-4: Git info ────────────────────────────────────────────────────────


def _run(cmd: list[str], cwd: Path | None = None) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd or _REPO_ROOT))
    return r.stdout.strip()


def step_git_info() -> GitInfo:
    """Steps 1-4: identify repo, branch, HEAD, inspect worktree."""
    # Step 1: repo name
    remote_url = _run(["git", "remote", "get-url", "origin"])
    repo = re.sub(r".*[/:]([^/]+?)(?:\.git)?$", r"\1", remote_url) or "unknown"
    # Extract owner/repo from any URL format (https, git@, proxy, etc.)
    owner_repo = re.search(r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?$", remote_url)
    remote = f"github.com/{owner_repo.group(1)}" if owner_repo else remote_url

    # Step 2: branch
    branch = _run(["git", "branch", "--show-current"]) or "HEAD (detached)"

    # Step 3: HEAD
    head = _run(["git", "rev-parse", "--short", "HEAD"])
    head_msg = _run(["git", "log", "-1", "--format=%s"])

    # Step 4: worktree
    status = _run(["git", "status", "--short"])
    lines = [ln for ln in status.splitlines() if ln.strip()]
    if not lines:
        worktree_clean = True
        worktree_summary = "Čistý worktree"
    else:
        worktree_clean = False
        staged = sum(1 for ln in lines if ln[0] != " " and ln[0] != "?")
        unstaged = sum(1 for ln in lines if ln[1] != " ")
        untracked = sum(1 for ln in lines if ln.startswith("?"))
        parts = []
        if staged:
            parts.append(f"{staged} staged")
        if unstaged:
            parts.append(f"{unstaged} unstaged")
        if untracked:
            parts.append(f"{untracked} untracked")
        worktree_summary = ", ".join(parts) if parts else f"{len(lines)} changes"

    return GitInfo(
        repo=repo,
        remote=remote,
        branch=branch,
        head=head,
        head_msg=head_msg,
        worktree_clean=worktree_clean,
        worktree_summary=worktree_summary,
    )


# ── Step 5: Project state ─────────────────────────────────────────────────────


def step_load_project_snapshot() -> str:
    """Step 5: Load key facts from project_snapshot.md."""
    path = _STARCORE_DIR / "memory" / "project_snapshot.md"
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    # Extract version line
    m = re.search(r"\|\s*Verze\s*\|\s*(\S+)", text)
    return m.group(1) if m else "unknown"


# ── Step 6: Last session ──────────────────────────────────────────────────────


def step_load_last_session() -> SessionEntry | None:
    """Step 6: Load the last (or active) session from ledger.yaml."""
    ledger_path = _STARCORE_DIR / "sessions" / "ledger.yaml"
    if not ledger_path.exists():
        return None
    with open(ledger_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    sessions_raw = data.get("sessions", [])
    if not sessions_raw:
        return None
    # Prefer active session; fall back to last
    entries = [SessionEntry.from_dict(s) for s in sessions_raw]
    active = next((s for s in entries if s.is_active()), None)
    return active or entries[-1]


# ── Step 7: Active risks ──────────────────────────────────────────────────────


_RISK_HEADER_RE = re.compile(r"^###\s+(R-\d+)\s+\S+\s+(.+)$")
_RISK_FIELD_RE = re.compile(r"^\s*-\s+\*\*([^*:]+):\*\*\s*(.+)$")

_SEVERITY_ORDER = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}


def parse_risks_content(content: str) -> list[RiskEntry]:
    """Parse risks.md content into OPEN RiskEntry list, sorted by severity."""
    risks: list[RiskEntry] = []
    current: dict[str, str] = {}  # id, title, Stav, Závažnost

    def _flush() -> None:
        rid = current.get("id")
        if rid:
            status = current.get("Stav", "UNKNOWN").split("/")[0].strip()
            severity = current.get("Závažnost", "LOW").strip()
            risks.append(RiskEntry(rid, current.get("title", ""), severity, status))

    for line in content.splitlines():
        m = _RISK_HEADER_RE.match(line)
        if m:
            _flush()
            current = {"id": m.group(1), "title": m.group(2).strip()}
            continue
        fm = _RISK_FIELD_RE.match(line)
        if fm and "id" in current:
            current[fm.group(1).strip()] = fm.group(2).strip()
    _flush()

    open_risks = [r for r in risks if "OPEN" in r.status]
    return sorted(open_risks, key=lambda r: _SEVERITY_ORDER.get(r.severity, 0), reverse=True)


def step_load_risks() -> list[RiskEntry]:
    """Step 7: Parse risks.md and return OPEN risks sorted by severity."""
    path = _STARCORE_DIR / "memory" / "risks.md"
    if not path.exists():
        return []
    return parse_risks_content(path.read_text(encoding="utf-8"))


# ── Step 8: Pending work ──────────────────────────────────────────────────────


def parse_pending_work_content(content: str) -> list[str]:
    """Extract P1 item headings from pending_work.md content string."""
    m = re.search(r"## P1[^\n]*\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if not m:
        return []
    items = re.findall(r"^###\s+(.+)$", m.group(1), re.MULTILINE)
    return [i for i in items if not re.match(r"^P\d", i)]


def step_load_pending_work() -> list[str]:
    """Step 8: Extract P1 items from pending_work.md."""
    path = _STARCORE_DIR / "memory" / "pending_work.md"
    if not path.exists():
        return []
    return parse_pending_work_content(path.read_text(encoding="utf-8"))


# ── Step 9: Decisions ─────────────────────────────────────────────────────────


def parse_decisions_content(content: str, limit: int = 3) -> list[str]:
    """Extract the most recent D-XXX headings from decisions.md content string."""
    matches = re.findall(r"^## (D-\d+\s+\S+\s+.+)$", content, re.MULTILINE)
    return list(reversed(matches[-limit:])) if matches else []


def step_load_decisions(limit: int = 3) -> list[str]:
    """Step 9: Load the most recent working decisions."""
    path = _STARCORE_DIR / "memory" / "decisions.md"
    if not path.exists():
        return []
    return parse_decisions_content(path.read_text(encoding="utf-8"), limit=limit)


# ── Step 10: Regression Sentinel ─────────────────────────────────────────────


def step_verify_sentinel() -> tuple[CheckState, str]:
    """
    Step 10: Run Regression Sentinel to detect drift vs baseline.
    Returns (worst_state, summary_detail).
    """
    try:
        from models import worst_state
        from regression_sentinel import _load_baseline, capture_snapshot, compare_snapshot

        baseline = _load_baseline()
        if not baseline:
            return CheckState.UNKNOWN, "Baseline nenalezena"
        current = capture_snapshot()
        results = compare_snapshot(current, baseline)
        if not results:
            return CheckState.UNKNOWN, "Žádné výsledky"
        ws = worst_state(results)
        fails = [r for r in results if r.state == CheckState.FAIL]
        warns = [r for r in results if r.state == CheckState.WARNING]
        if fails:
            detail = f"REGRESE: {', '.join(r.name for r in fails)}"
        elif warns:
            detail = f"Varování: {', '.join(r.name for r in warns)}"
        else:
            detail = f"✓ {len(results)}/{len(results)} dimenzí bez regrese"
        return ws, detail
    except Exception as exc:
        return CheckState.UNKNOWN, f"Chyba: {exc}"


# ── Step 11: GitHub state ─────────────────────────────────────────────────────


def step_verify_github() -> tuple[str, list[str]]:
    """
    Step 11: Run GITHUB gate from Release Readiness Engine.
    Returns (verdict, list_of_blockers).
    """
    try:
        from release_readiness import check_github, overall_verdict

        results = check_github(quick=False)
        verdict = overall_verdict({"GITHUB": results})
        blockers = [r.detail for r in results if r.state in (CheckState.FAIL, CheckState.WARNING)]
        return verdict, blockers
    except Exception as exc:
        return "UNKNOWN", [f"Chyba GitHub gate: {exc}"]


# ── Collect all ───────────────────────────────────────────────────────────────


def collect_startup_state(quick: bool = False) -> StartupState:
    """Execute all 12 startup steps and return consolidated state."""
    git = step_git_info()
    last_session = step_load_last_session()
    open_risks = step_load_risks()
    p1_items = step_load_pending_work()
    recent_decisions = step_load_decisions()

    if quick:
        sentinel_state = CheckState.UNKNOWN
        sentinel_detail = "Přeskočeno (--quick)"
        release_verdict = "UNKNOWN"
        release_blockers = ["Přeskočeno (--quick)"]
    else:
        sentinel_state, sentinel_detail = step_verify_sentinel()
        release_verdict, release_blockers = step_verify_github()

    return StartupState(
        git=git,
        last_session=last_session,
        open_risks=open_risks,
        p1_items=p1_items,
        recent_decisions=recent_decisions,
        sentinel_state=sentinel_state,
        sentinel_detail=sentinel_detail,
        release_verdict=release_verdict,
        release_blockers=release_blockers,
        quick=quick,
    )


# ── Report formatting ─────────────────────────────────────────────────────────


_VERDICT_CZ: dict[str, str] = {
    "RELEASE_READY": "✓ PŘIPRAVEN K RELEASE",
    "RELEASE_READY_WITH_WARNINGS": "⚠ PŘIPRAVEN (s varováními)",
    "NOT_RELEASE_READY": "✗ NENÍ PŘIPRAVEN",
    "BLOCKED": "✗ BLOKOVÁN",
    "UNKNOWN": "? NEOVĚŘENO",
}

_SENTINEL_ICONS: dict[str, str] = {
    "PASS": "✓ PASS",
    "WARNING": "⚠ WARNING",
    "FAIL": "✗ FAIL",
    "UNKNOWN": "? UNKNOWN",
    "NOT_APPLICABLE": "— N/A",
}


def _fmt_session(s: SessionEntry | None) -> str:
    if s is None:
        return "Žádná předchozí session"
    status = "aktivní" if s.is_active() else "ukončena"
    date_part = s.start_time[:10] if s.start_time else "?"
    req_count = len(s.user_requests)
    return f"{s.session_id} ({date_part}, {status}, {req_count} požadavků)"


def _fmt_next_action(state: StartupState) -> str:
    """Derive recommended next action from state."""
    # Prefer the last session's recorded next_action
    if state.last_session and state.last_session.next_action:
        return state.last_session.next_action
    # Fall back to P1 if available
    if state.p1_items:
        return state.p1_items[0]
    # Fall back to sentinel fix
    if state.sentinel_state == CheckState.FAIL:
        return "Opravit regrese detekované Sentinelem"
    return "Spustit audit: uv run python .starcore/scripts/qc_engine.py run --quick"


def format_startup_report(state: StartupState) -> str:
    """Format the Czech startup report with 11 fields + 6-option menu."""
    g = state.git

    # Git line
    git_line = f"{g.worktree_summary}"
    if not g.worktree_clean:
        git_line += " — POZOR: uncommitted changes"

    # Risks summary
    if state.open_risks:
        risk_parts = [f"{r.id} ({r.severity})" for r in state.open_risks[:5]]
        risks_line = ", ".join(risk_parts)
        if len(state.open_risks) > 5:
            risks_line += f" +{len(state.open_risks) - 5} dalších"
    else:
        risks_line = "Žádná aktivní rizika"

    # Blockers from P1 + sentinel
    blockers: list[str] = []
    if state.p1_items:
        blockers.append(f"P1: {state.p1_items[0]}")
    if state.sentinel_state == CheckState.FAIL:
        blockers.append(f"Sentinel: {state.sentinel_detail}")
    blockers_line = " | ".join(blockers) if blockers else "Žádné blokery"

    # Pending tasks
    if state.p1_items:
        tasks_line = "; ".join(state.p1_items[:3])
        if len(state.p1_items) > 3:
            tasks_line += f" (+ {len(state.p1_items) - 3} dalších)"
    else:
        tasks_line = "Žádné nedokončené P1 úkoly"

    # Last decision
    last_decision = state.recent_decisions[0] if state.recent_decisions else "—"

    # QC state
    sentinel_icon = _SENTINEL_ICONS.get(str(state.sentinel_state), "?")
    sentinel_line = f"{sentinel_icon}  {state.sentinel_detail}"

    verdict_cz = _VERDICT_CZ.get(state.release_verdict, state.release_verdict)
    release_line = verdict_cz
    if state.release_blockers and "Přeskočeno" not in state.release_blockers[0]:
        release_line += f"\n                     {state.release_blockers[0]}"

    # Next action
    next_action = _fmt_next_action(state)

    # Build report
    lines = [
        "",
        _SEP,
        "STARCORE SESSION STATUS",
        _SEP,
        "",
        f"Projekt:             {g.repo}",
        f"                     {g.remote}",
        f"Branch:              {g.branch}",
        f"HEAD:                {g.head} — {g.head_msg}",
        f"Git:                 {git_line}",
        f"Poslední session:    {_fmt_session(state.last_session)}",
        f"Aktivní rizika:      {risks_line}",
        f"Blokery:             {blockers_line}",
        f"Nedokončené úkoly:   {tasks_line}",
        f"Poslední rozhodnutí: {last_decision}",
        f"QC Sentinel:         {sentinel_line}",
        f"Release:             {release_line}",
        f"Doporučený krok:     {next_action}",
        "",
        _SEP2,
        "VOLBY:",
        "  [1] Pokračovat podle doporučení",
        "  [2] Spustit QC audit (sentinel + release readiness)",
        "  [3] Zobrazit stav projektu",
        "  [4] Zobrazit rizika a pending work",
        "  [5] Zobrazit historii session",
        "  [6] Vlastní instrukce",
        _SEP,
        "",
    ]
    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="startup_protocol",
        description="STARCORE Startup Protocol — 12-step session initialization",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Přeskočit pomalé QC kontroly (sentinel, release readiness)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Výstup ve formátu JSON (pro strojové zpracování)",
    )
    args = parser.parse_args()

    state = collect_startup_state(quick=args.quick)

    if args.as_json:
        print(json.dumps(state.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_startup_report(state))

    # Exit code: 1 if sentinel FAIL, otherwise 0
    return 1 if state.sentinel_state == CheckState.FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
