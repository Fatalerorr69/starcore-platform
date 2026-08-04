#!/usr/bin/env python3
"""
STARCORE release helper.

Commands
--------
check-changelog
    Fail with exit code 1 when the [Unreleased] section in CHANGELOG.md
    has no content (no ### subsection with at least one bullet).
    Used as a CI gate on every PR so contributors don't forget to add entries.

bump VERSION
    Cut a release from [Unreleased]:
      1. Validate [Unreleased] is non-empty.
      2. Move [Unreleased] content to ## [VERSION] — YYYY-MM-DD.
      3. Insert a fresh empty [Unreleased] placeholder.
      4. Update `version = "..."` in pyproject.toml.
      5. Update _SERVICE_VERSION in packages/core/tracing.py.

    Does NOT commit or tag — that is left to the caller.

Usage
-----
    uv run python scripts/release.py check-changelog
    uv run python scripts/release.py bump 0.5.0
"""

from __future__ import annotations

import re
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
PYPROJECT = REPO_ROOT / "pyproject.toml"
TRACING = REPO_ROOT / "packages" / "core" / "tracing.py"

_UNRELEASED_RE = re.compile(r"^## \[Unreleased\]", re.MULTILINE)
_NEXT_SECTION_RE = re.compile(r"^## \[", re.MULTILINE)
_SUBSECTION_RE = re.compile(r"^### \S", re.MULTILINE)


# ── helpers ──────────────────────────────────────────────────────────────────


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _unreleased_body(changelog: str) -> str:
    """Return the text between [Unreleased] and the next ## section."""
    m = _UNRELEASED_RE.search(changelog)
    if not m:
        sys.exit("ERROR: [Unreleased] section not found in CHANGELOG.md")
    after = changelog[m.end():]
    next_sec = _NEXT_SECTION_RE.search(after)
    return after[: next_sec.start()] if next_sec else after


def _has_content(body: str) -> bool:
    """True when the body contains at least one ### subsection."""
    return bool(_SUBSECTION_RE.search(body))


# ── commands ──────────────────────────────────────────────────────────────────


def cmd_check_changelog() -> None:
    """CI gate: fail when [Unreleased] is empty."""
    body = _unreleased_body(_read(CHANGELOG))
    if not _has_content(body):
        print(
            "ERROR: [Unreleased] section in CHANGELOG.md is empty.\n"
            "Add at least one ### subsection (Added / Changed / Fixed / Security)\n"
            "before merging this pull request.",
            file=sys.stderr,
        )
        sys.exit(1)
    print("CHANGELOG gate passed — [Unreleased] has content.")


def cmd_bump(version: str) -> None:
    """Cut a release: move [Unreleased] → [version], bump version strings."""
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        sys.exit(f"ERROR: version must be X.Y.Z, got {version!r}")

    changelog = _read(CHANGELOG)
    body = _unreleased_body(changelog)

    if not _has_content(body):
        sys.exit("ERROR: [Unreleased] section is empty — nothing to release.")

    today = datetime.now(tz=UTC).strftime("%Y-%m-%d")
    versioned_header = f"## [{version}] — {today}"
    new_unreleased = "## [Unreleased]\n\n"

    # Replace ## [Unreleased]<body> with the new unreleased stub + versioned section
    unreleased_match = _UNRELEASED_RE.search(changelog)
    assert unreleased_match  # already checked in _unreleased_body
    start = unreleased_match.start()
    body_end = unreleased_match.end() + len(body)
    updated = (
        changelog[:start]
        + new_unreleased
        + versioned_header
        + body
        + changelog[body_end:]
    )
    _write(CHANGELOG, updated)
    print(f"CHANGELOG.md: [Unreleased] → [{version}] — {today}")

    # pyproject.toml — version = "X.Y.Z"
    pyproject = _read(PYPROJECT)
    new_pyproject, n = re.subn(
        r'^(version\s*=\s*")[^"]*(")',
        rf'\g<1>{version}\g<2>',
        pyproject,
        count=1,
        flags=re.MULTILINE,
    )
    if not n:
        sys.exit("ERROR: could not find version field in pyproject.toml")
    _write(PYPROJECT, new_pyproject)
    print(f"pyproject.toml: version → {version!r}")

    # packages/core/tracing.py — _SERVICE_VERSION = "X.Y.Z"
    tracing = _read(TRACING)
    new_tracing, n = re.subn(
        r'^(_SERVICE_VERSION\s*=\s*")[^"]*(")',
        rf'\g<1>{version}\g<2>',
        tracing,
        count=1,
        flags=re.MULTILINE,
    )
    if not n:
        sys.exit("ERROR: could not find _SERVICE_VERSION in packages/core/tracing.py")
    _write(TRACING, new_tracing)
    print(f"packages/core/tracing.py: _SERVICE_VERSION → {version!r}")

    print(f"\nRelease {version} prepared. Next steps:")
    print("  git add CHANGELOG.md pyproject.toml packages/core/tracing.py")
    print(f"  git commit -m 'chore: release v{version}'")
    print(f"  git tag v{version}")
    print(f"  git push origin main v{version}")


# ── entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    command = args[0]
    if command == "check-changelog":
        if len(args) != 1:
            sys.exit("Usage: release.py check-changelog")
        cmd_check_changelog()
    elif command == "bump":
        if len(args) != 2:
            sys.exit("Usage: release.py bump VERSION")
        cmd_bump(args[1])
    else:
        sys.exit(f"Unknown command {command!r}. Use check-changelog or bump VERSION.")


if __name__ == "__main__":
    main()
