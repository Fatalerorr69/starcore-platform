#!/usr/bin/env python3
"""
STARCORE Doctor — standalone local quality gate runner.

Runs all CI gates locally and reports PASS/FAIL for each.
Exits 0 when all gates pass, 1 if any fail.

Usage:
    uv run python scripts/doctor.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

GATES: list[tuple[str, list[str]]] = [
    ("Lockfile", ["uv", "lock", "--check"]),
    ("Ruff lint", ["uv", "run", "ruff", "check", "."]),
    ("Ruff format", ["uv", "run", "ruff", "format", "--check", "."]),
    ("Pyright", ["uv", "run", "pyright"]),
    ("pip-audit", ["uv", "run", "pip-audit"]),
    ("Tests", ["uv", "run", "pytest", "-q", "--tb=short"]),
]

_COL = 16


def _run(cmd: list[str]) -> tuple[bool, str]:
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    ok = proc.returncode == 0
    out = (proc.stdout + proc.stderr).strip()
    return ok, out


def main() -> int:
    print("STARCORE Doctor — Quality Gates\n")

    results: list[tuple[str, bool, str]] = []
    for name, cmd in GATES:
        print(f"  {name:<{_COL}} ...", end="", flush=True)
        ok, out = _run(cmd)
        print(f"\r  {name:<{_COL}} {'PASS' if ok else 'FAIL'}")
        results.append((name, ok, out))

    failed = [(n, o) for n, ok, o in results if not ok]
    print()

    if failed:
        print(f"RESULT: {len(failed)}/{len(results)} gate(s) FAILED\n")
        for name, out in failed:
            print(f"--- {name} ---")
            print(out[:3000])
            print()
        return 1

    print(f"RESULT: ALL {len(results)} GATES PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
