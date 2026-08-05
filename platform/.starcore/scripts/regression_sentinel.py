#!/usr/bin/env python3
"""
STARCORE Regression Sentinel CLI.

Detects regressions by comparing the current repository state against the
committed baseline in .starcore/state/regression_baseline.json.

Použití:
  uv run python .starcore/scripts/regression_sentinel.py check
  uv run python .starcore/scripts/regression_sentinel.py check --full
  uv run python .starcore/scripts/regression_sentinel.py update
  uv run python .starcore/scripts/regression_sentinel.py diff
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent
_BASELINE_PATH = _SCRIPT_DIR.parent / "state" / "regression_baseline.json"

sys.path.insert(0, str(_SCRIPT_DIR))
from models import CheckResult, CheckState  # noqa: E402

# ── Probe functions — return actual current values ────────────────────────────


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd or _REPO_ROOT))
    return r.returncode, (r.stdout + r.stderr).strip()


def probe_test_count() -> int:
    """Count tests via pytest --collect-only (no execution, ~1.5s)."""
    _, out = _run(["uv", "run", "pytest", "--collect-only", "-q", "--tb=no"])
    m = re.search(r"(\d+)\s+tests? collected", out)
    return int(m.group(1)) if m else -1


def probe_api_routes() -> int:
    """Count HTTP/WebSocket route decorators in core/main.py and core/routers/."""
    route_re = re.compile(
        r"^@(?:app|router)\.(get|post|put|delete|patch|websocket)\(",
        re.MULTILINE,
    )
    count = 0
    core_dir = _REPO_ROOT / "packages" / "core"
    for py_file in [core_dir / "main.py"] + list((core_dir / "routers").glob("*.py")):
        if py_file.exists():
            count += len(route_re.findall(py_file.read_text()))
    return count


def probe_cli_commands() -> int:
    """Count @app.command() decorators in apps/cli/main.py."""
    cli_py = _REPO_ROOT / "apps" / "cli" / "main.py"
    if not cli_py.exists():
        return -1
    text = cli_py.read_text()
    return len(re.findall(r"@\w+\.command\(\)", text))


def probe_config_fields() -> int:
    """Count Settings fields (lines starting with 4-space-indented identifier)."""
    cfg = _REPO_ROOT / "packages" / "core" / "config.py"
    if not cfg.exists():
        return -1
    text = cfg.read_text()
    # Settings field definitions: 4-space indent + identifier + : + optional annotation
    return len(re.findall(r"^\s{4}\w+\s*[=:]", text, re.MULTILINE))


def probe_adr_count() -> int:
    """Count ADR markdown files in docs/adr/."""
    adr_dir = _REPO_ROOT / "docs" / "adr"
    if not adr_dir.exists():
        return -1
    return len(list(adr_dir.glob("ADR-*.md")))


def probe_workflow_count() -> int:
    """Count .github/workflows/*.yml files."""
    wf_dir = _REPO_ROOT / ".github" / "workflows"
    if not wf_dir.exists():
        return -1
    return len(list(wf_dir.glob("*.yml")))


def probe_lock_sync() -> bool:
    """Return True if uv.lock is in sync with pyproject.toml."""
    rc, _ = _run(["uv", "lock", "--check"])
    return rc == 0


# ── Snapshot (current state dict) ────────────────────────────────────────────


def capture_snapshot() -> dict:
    return {
        "test_count": probe_test_count(),
        "api_routes": probe_api_routes(),
        "cli_commands": probe_cli_commands(),
        "config_fields": probe_config_fields(),
        "adr_count": probe_adr_count(),
        "workflow_count": probe_workflow_count(),
        "lock_sync": probe_lock_sync(),
    }


# ── Comparison logic ──────────────────────────────────────────────────────────


def _load_baseline() -> dict:
    if not _BASELINE_PATH.exists():
        return {}
    with open(_BASELINE_PATH) as f:
        return json.load(f)


def _cmp_count(
    name: str,
    current: int,
    baseline: int | None,
    *,
    direction: str = "down",  # "down" = regression if current < baseline
    delta_warn: int = 0,
) -> CheckResult:
    """Compare a numeric probe against baseline."""
    if baseline is None:
        return CheckResult(
            name=name,
            state=CheckState.UNKNOWN,
            detail=f"Baseline pro '{name}' chybí",
        )
    if current < 0:
        return CheckResult(
            name=name,
            state=CheckState.UNKNOWN,
            detail=f"Probe '{name}' selhalo",
        )
    diff = current - baseline
    if direction == "down" and diff < -delta_warn:
        return CheckResult(
            name=name,
            state=CheckState.FAIL,
            detail=f"REGRESE: {name} {baseline} → {current} (Δ{diff})",
            evidence=[f"baseline={baseline}", f"current={current}"],
        )
    if direction == "up" and diff > delta_warn:
        return CheckResult(
            name=name,
            state=CheckState.WARNING,
            detail=f"NÁRŮST: {name} {baseline} → {current} (+{diff})",
            evidence=[f"baseline={baseline}", f"current={current}"],
        )
    if diff != 0:
        return CheckResult(
            name=name,
            state=CheckState.WARNING,
            detail=f"Změna: {name} {baseline} → {current} (Δ{diff:+d})",
            evidence=[f"baseline={baseline}", f"current={current}"],
        )
    return CheckResult(
        name=name,
        state=CheckState.PASS,
        detail=f"{name} beze změny ({current})",
    )


def compare_snapshot(current: dict, baseline_data: dict) -> list[CheckResult]:
    """
    Produce a CheckResult for each tracked dimension.
    baseline_data is the full baseline JSON (may contain nested keys).
    """
    results: list[CheckResult] = []

    # Resolve baseline values — may live in sentinel sub-key or top-level
    sentinel = baseline_data.get("sentinel", {})

    def _base(key: str, fallback=None):
        return sentinel.get(key, baseline_data.get(key, fallback))

    # Test count
    baseline_tests = _base("test_count", baseline_data.get("tests", {}).get("total"))
    results.append(_cmp_count("test_count", current["test_count"], baseline_tests, delta_warn=0))

    # API routes
    results.append(
        _cmp_count("api_routes", current["api_routes"], _base("api_routes"), direction="both")
    )

    # CLI commands
    results.append(
        _cmp_count("cli_commands", current["cli_commands"], _base("cli_commands"), direction="both")
    )

    # Config fields
    results.append(
        _cmp_count(
            "config_fields", current["config_fields"], _base("config_fields"), direction="both"
        )
    )

    # ADR count (only decrease is a regression)
    results.append(
        _cmp_count("adr_count", current["adr_count"], _base("adr_count"), direction="down")
    )

    # Workflow count (only decrease is a regression)
    results.append(
        _cmp_count(
            "workflow_count", current["workflow_count"], _base("workflow_count"), direction="down"
        )
    )

    # Lock sync
    lock_sync = current["lock_sync"]
    if lock_sync:
        results.append(
            CheckResult("lock_sync", CheckState.PASS, "uv.lock konzistentní s pyproject.toml")
        )
    else:
        results.append(
            CheckResult(
                "lock_sync",
                CheckState.FAIL,
                "uv.lock NENÍ konzistentní — spusť 'uv lock'",
            )
        )

    return results


# ── CLI commands ──────────────────────────────────────────────────────────────

_SEP = "─" * 72
_LABELS = {
    "test_count": "Testy         ",
    "api_routes": "API routes    ",
    "cli_commands": "CLI příkazy  ",
    "config_fields": "Config fields ",
    "adr_count": "ADR soubory  ",
    "workflow_count": "CI workflows  ",
    "lock_sync": "Lock sync     ",
}


def cmd_check(args: argparse.Namespace) -> int:
    print(f"\n{_SEP}")
    print("STARCORE Regression Sentinel")
    print(_SEP)

    baseline = _load_baseline()
    if not baseline:
        print("CHYBA: Baseline nenalezena. Spusť 'update' nejprve.", file=sys.stderr)
        return 1

    print("Sbírám aktuální stav…")
    current = capture_snapshot()

    results = compare_snapshot(current, baseline)

    print(f"\n{'Dimenze':<18} {'Stav':<12} Detail")
    print("─" * 65)
    any_fail = False
    for r in results:
        label = _LABELS.get(r.name, r.name[:18])
        print(f"{label:<18} {r.icon} {r.state:<10} {r.detail}")
        if r.state == CheckState.FAIL:
            any_fail = True

    print(_SEP)
    if any_fail:
        print("VÝSLEDEK: FAIL — regrese detekována!")
        return 1

    _prio = {"FAIL": 4, "UNKNOWN": 3, "WARNING": 2, "PASS": 1, "NOT_APPLICABLE": 0}
    worst = max(results, key=lambda r: _prio.get(str(r.state), 0))
    print(f"VÝSLEDEK: {worst.icon} {worst.state}")
    return 0


def cmd_update(_args: argparse.Namespace) -> int:
    """Capture current state and write it to the sentinel section of baseline."""
    baseline = _load_baseline()
    current = capture_snapshot()
    baseline["sentinel"] = current
    with open(_BASELINE_PATH, "w") as f:
        json.dump(baseline, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("OK: Sentinel baseline aktualizován.")
    for k, v in current.items():
        print(f"  {k}: {v}")
    return 0


def cmd_diff(_args: argparse.Namespace) -> int:
    """Show diff between current state and baseline."""
    baseline = _load_baseline()
    current = capture_snapshot()
    sentinel = baseline.get("sentinel", {})

    print(f"\n{'Dimenze':<18} {'Baseline':>12} {'Aktuální':>12} {'Δ':>6}")
    print("─" * 52)
    for key, cur_val in current.items():
        base_val = sentinel.get(key)
        if isinstance(cur_val, bool):
            delta = ""
            diff_str = "→ " + ("OK" if cur_val else "FAIL")
        elif base_val is not None and isinstance(cur_val, int):
            delta_n = cur_val - base_val
            delta = f"{delta_n:+d}" if delta_n != 0 else "="
            diff_str = ""
        else:
            delta = "?"
            diff_str = ""
        base_str = str(base_val) if base_val is not None else "?"
        cur_str = str(cur_val)
        label = _LABELS.get(key, key)[:18]
        print(f"{label:<18} {base_str:>12} {cur_str:>12} {delta:>6}  {diff_str}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="regression_sentinel",
        description="STARCORE Regression Sentinel",
    )
    sub = parser.add_subparsers(dest="command")

    p_check = sub.add_parser("check", help="Porovnat aktuální stav s baseline")
    p_check.add_argument("--full", action="store_true", help="Spustit i pomalé kontroly")

    sub.add_parser("update", help="Aktualizovat sentinel baseline")
    sub.add_parser("diff", help="Zobrazit diff aktuální vs baseline")

    args = parser.parse_args()
    dispatch = {"check": cmd_check, "update": cmd_update, "diff": cmd_diff}

    if args.command not in dispatch:
        parser.print_help()
        return 1
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
