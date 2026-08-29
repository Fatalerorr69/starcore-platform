#!/usr/bin/env python3
"""
STARCORE Repository Governance Discovery Tool.

Read-only classification of top-level repository directories per
ADR-018 (platform/ vs. repository root boundary), ADR-020 (legacy root
layer freeze), and ADR-025 (Discovery First Principle / Repository
Integrity Gate).

This tool never deletes, moves, renames, or "fixes" anything. Its only
write operation is overwriting the state snapshot at
.starcore/state/repository_map.json — nothing else on disk is ever
touched.

Použití:
  uv run python .starcore/scripts/repository_map.py scan
  uv run python .starcore/scripts/repository_map.py scan --json
  uv run python .starcore/scripts/repository_map.py diff
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).parent
_STARCORE_DIR = _SCRIPT_DIR.parent
_PLATFORM_ROOT = _STARCORE_DIR.parent
_REPO_ROOT = _PLATFORM_ROOT.parent
_STATE_PATH = _STARCORE_DIR / "state" / "repository_map.json"

_SCHEMA_VERSION = "1.0"


class Classification(StrEnum):
    PRODUCTION = "PRODUCTION"
    DOCUMENTATION = "DOCUMENTATION"
    EXPERIMENTAL = "EXPERIMENTAL"
    LEGACY = "LEGACY"
    UNKNOWN = "UNKNOWN"


# Per ADR-020 (Legacy Root Layer Freeze) — top-level directories explicitly
# classified as frozen legacy scaffolding by the STARCORE SAEF Integration
# Discovery Report (2026-08-06). This list is intentionally static: a
# newly created top-level directory is never silently assumed to be
# legacy — it is classified UNKNOWN until a human decision (a new ADR or
# an explicit update to this list) says otherwise. DOCUMENTATION and
# EXPERIMENTAL are kept in the enum for future use (e.g. a future
# `edge-node/` directory per ADR-024 before it earns PRODUCTION status)
# even though no current top-level directory maps to them.
_LEGACY_ALLOWLIST: frozenset[str] = frozenset(
    {
        "agents",
        "ai_core",
        "ai_runtime",
        "api_gateway",
        "automation",
        "autonomous",
        "backups",
        "bin",
        "bundles_7x",
        "cli",
        "config",
        "control_center",
        "core",
        "distributed",
        "github_intelligence",
        "hardening",
        "installers",
        "intelligence",
        "knowledge",
        "knowledge_engine",
        "mission_engine",
        "performance",
        "plugins",
        "prompts",
        "registry",
        "runtime",
        "sdk",
        "security",
        "sessions",
        "starcore",
        "studio",
        "templates",
        "tools",
    }
)

# Top-level entries excluded from classification entirely — repository
# tooling directories, not product/legacy content in the sense this tool
# classifies. Never extended to include content directories.
_SKIP_NAMES: frozenset[str] = frozenset({".git", ".github", "site"})


@dataclass
class RepositoryEntry:
    path: str
    classification: Classification
    reason: str
    detected_files: list[str] = field(default_factory=list)
    git_activity: dict[str, Any] = field(default_factory=dict)
    confidence: str = "UNKNOWN"
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "classification": str(self.classification),
            "reason": self.reason,
            "detected_files": self.detected_files,
            "git_activity": self.git_activity,
            "confidence": self.confidence,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RepositoryEntry:
        return cls(
            path=data["path"],
            classification=Classification(data.get("classification", "UNKNOWN")),
            reason=data.get("reason", ""),
            detected_files=data.get("detected_files", []),
            git_activity=data.get("git_activity", {}),
            confidence=data.get("confidence", "UNKNOWN"),
            notes=data.get("notes", ""),
        )


def _run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))
    return r.returncode, (r.stdout + r.stderr).strip()


def git_activity(repo_root: Path, rel_name: str) -> dict[str, Any]:
    """Read-only git metadata for a top-level path: commit count and last commit date.

    Never mutates repository state — only `git log` is invoked.
    """
    _, count_out = _run(["git", "log", "--oneline", "--all", "--", rel_name], cwd=repo_root)
    commit_count = len([line for line in count_out.splitlines() if line.strip()])
    _, date_out = _run(["git", "log", "-1", "--format=%cI", "--", rel_name], cwd=repo_root)
    last_commit = date_out.strip() or None
    return {"commit_count": commit_count, "last_commit": last_commit}


def _sample_files(path: Path, limit: int = 5) -> list[str]:
    """Non-recursive sample of immediate children, for the 'detected_files' field."""
    try:
        children = sorted(p.name for p in path.iterdir())
    except OSError:
        return []
    return children[:limit]


def classify(name: str) -> tuple[Classification, str, str]:
    """Return (classification, reason, confidence) for a top-level directory name.

    Pure function — no filesystem or git access.
    """
    if name == "platform":
        return (
            Classification.PRODUCTION,
            "Sole authoritative product per ADR-018; tested, CI-gated, "
            "carries its own ADR series and .starcore/ knowledge layer.",
            "HIGH",
        )
    if name in _LEGACY_ALLOWLIST:
        return (
            Classification.LEGACY,
            "Frozen legacy root scaffolding per ADR-020; classified during "
            "the STARCORE SAEF Integration Discovery Report (2026-08-06).",
            "HIGH",
        )
    return (
        Classification.UNKNOWN,
        "Not present in the ADR-020 legacy allowlist and not 'platform/'. "
        "Requires a human classification decision — never silently "
        "assumed to be legacy or safe.",
        "LOW",
    )


def scan(
    *,
    repo_root: Path = _REPO_ROOT,
    state_path: Path = _STATE_PATH,
    write: bool = True,
) -> dict[str, Any]:
    """
    Classify every top-level directory under repo_root.

    Read-only except for the single write this function performs when
    write=True: overwriting state_path. No file or directory anywhere in
    the repository is ever deleted, moved, or otherwise modified by this
    function — no os.remove, no Path.unlink, no shutil.move/rmtree, no
    `git mv`/`git rm` is ever called.
    """
    entries: list[RepositoryEntry] = []
    for child in sorted(repo_root.iterdir(), key=lambda p: p.name):
        if not child.is_dir() or child.name in _SKIP_NAMES:
            continue
        classification, reason, confidence = classify(child.name)
        entries.append(
            RepositoryEntry(
                path=f"{child.name}/",
                classification=classification,
                reason=reason,
                detected_files=[f"{child.name}/{f}" for f in _sample_files(child)],
                git_activity=git_activity(repo_root, child.name),
                confidence=confidence,
                notes="",
            )
        )

    _, head = _run(["git", "rev-parse", "--short", "HEAD"], cwd=repo_root)
    snapshot: dict[str, Any] = {
        "schema_version": _SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo_root_commit": head.strip(),
        "entries": [e.to_dict() for e in entries],
    }

    if write:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(state_path, "w") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
            f.write("\n")

    return snapshot


def load_state(state_path: Path = _STATE_PATH) -> dict[str, Any] | None:
    if not state_path.exists():
        return None
    with open(state_path) as f:
        return json.load(f)


def compute_diff(old: dict[str, Any] | None, new: dict[str, Any]) -> dict[str, Any]:
    """Pure comparison between a previous snapshot (or None) and a new one.

    Returns a dict with 'added', 'removed', 'changed' path lists and a
    'has_unknown' flag. Never reads or writes any file itself.
    """
    old_entries = {e["path"]: e for e in (old or {}).get("entries", [])}
    new_entries = {e["path"]: e for e in new["entries"]}

    added = sorted(set(new_entries) - set(old_entries))
    removed = sorted(set(old_entries) - set(new_entries))
    changed = sorted(
        path
        for path in set(new_entries) & set(old_entries)
        if old_entries[path]["classification"] != new_entries[path]["classification"]
    )
    has_unknown = any(
        e["classification"] == str(Classification.UNKNOWN) for e in new_entries.values()
    )

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "old_entries": old_entries,
        "new_entries": new_entries,
        "has_unknown": has_unknown,
    }


def cmd_scan(args: argparse.Namespace) -> int:
    snapshot = scan(write=True)
    if args.json:
        print(json.dumps(snapshot, indent=2, ensure_ascii=False))
        return 0

    print(f"\nSTARCORE Repository Map — {snapshot['generated_at']}")
    print(f"HEAD: {snapshot['repo_root_commit']}\n")
    print(f"{'Path':<22} {'Classification':<16} {'Confidence':<10} {'Commits':>8}")
    print("─" * 60)
    for entry in snapshot["entries"]:
        activity = entry["git_activity"]
        print(
            f"{entry['path']:<22} {entry['classification']:<16} "
            f"{entry['confidence']:<10} {activity.get('commit_count', 0):>8}"
        )
    print(f"\nZapsáno: {_STATE_PATH}")
    return 0


def cmd_diff(_args: argparse.Namespace) -> int:
    old = load_state()
    new = scan(write=False)
    result = compute_diff(old, new)

    if old is None:
        print("Žádný předchozí stav nenalezen — spusťte nejprve 'scan'.\n")

    print("NOVÉ ADRESÁŘE:")
    for path in result["added"]:
        print(f"  + {path} → {result['new_entries'][path]['classification']}")
    if not result["added"]:
        print("  (žádné)")

    print("\nODSTRANĚNÉ ADRESÁŘE:")
    for path in result["removed"]:
        print(f"  - {path} (byl: {result['old_entries'][path]['classification']})")
    if not result["removed"]:
        print("  (žádné)")

    print("\nZMĚNA KLASIFIKACE:")
    for path in result["changed"]:
        old_c = result["old_entries"][path]["classification"]
        new_c = result["new_entries"][path]["classification"]
        print(f"  ~ {path}: {old_c} → {new_c}")
    if not result["changed"]:
        print("  (žádná)")

    if result["has_unknown"]:
        print("\nUNKNOWN klasifikace nalezena — vyžaduje lidské rozhodnutí.")
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="repository_map",
        description="STARCORE Repository Governance Discovery Tool (read-only)",
    )
    sub = parser.add_subparsers(dest="command")

    p_scan = sub.add_parser("scan", help="Klasifikovat top-level adresáře a zapsat state")
    p_scan.add_argument("--json", action="store_true", help="Vypsat JSON místo tabulky")

    sub.add_parser("diff", help="Porovnat aktuální stav s předchozím repository_map.json")

    args = parser.parse_args()
    dispatch = {"scan": cmd_scan, "diff": cmd_diff}

    if args.command not in dispatch:
        parser.print_help()
        return 1
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
