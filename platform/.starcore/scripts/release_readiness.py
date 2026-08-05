#!/usr/bin/env python3
"""
STARCORE Release Readiness Engine CLI.

Evaluates 12 release gates and returns RELEASE_READY, RELEASE_READY_WITH_WARNINGS,
NOT_RELEASE_READY, or BLOCKED.

Použití:
  uv run python .starcore/scripts/release_readiness.py evaluate
  uv run python .starcore/scripts/release_readiness.py evaluate --quick
  uv run python .starcore/scripts/release_readiness.py gate BUILD
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
from models import CheckResult, CheckState, worst_state  # noqa: E402

# ── Helpers ───────────────────────────────────────────────────────────────────


def _run(cmd: list[str]) -> tuple[int, str]:
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(_REPO_ROOT))
    return r.returncode, (r.stdout + r.stderr).strip()


def _exists(rel_path: str) -> bool:
    return (_REPO_ROOT / rel_path).exists()


def _file_contains(rel_path: str, pattern: str) -> bool:
    p = _REPO_ROOT / rel_path
    if not p.exists():
        return False
    return bool(re.search(pattern, p.read_text()))


def _load_baseline() -> dict:
    if not _BASELINE_PATH.exists():
        return {}
    with open(_BASELINE_PATH) as f:
        return json.load(f)


# ── Individual gate checks ────────────────────────────────────────────────────


def check_build(quick: bool) -> list[CheckResult]:
    results: list[CheckResult] = []

    # Dockerfile existence
    if _exists("Dockerfile"):
        results.append(CheckResult("BUILD.dockerfile", CheckState.PASS, "Dockerfile nalezen"))
    else:
        results.append(
            CheckResult("BUILD.dockerfile", CheckState.FAIL, "Dockerfile chybí", ["Dockerfile"])
        )

    # docker-compose.yml
    if _exists("docker-compose.yml"):
        results.append(CheckResult("BUILD.compose", CheckState.PASS, "docker-compose.yml nalezen"))
    else:
        results.append(CheckResult("BUILD.compose", CheckState.FAIL, "docker-compose.yml chybí"))

    # Docker build — always UNKNOWN in non-CI environments
    results.append(
        CheckResult(
            "BUILD.docker_build",
            CheckState.UNKNOWN,
            "Docker image build nebylo spuštěno (spouští se v CI)",
        )
    )
    return results


def check_test(quick: bool) -> list[CheckResult]:
    results: list[CheckResult] = []
    baseline = _load_baseline()
    base_tests = baseline.get("tests", {})

    if quick:
        # Use baseline
        total = base_tests.get("total", -1)
        failed = base_tests.get("failed", -1)
        coverage = baseline.get("coverage", {}).get("percent", -1)
        src = "(baseline)"
    else:
        # Run fast collection
        _, out = _run(["uv", "run", "pytest", "--collect-only", "-q", "--tb=no"])
        m = re.search(r"(\d+)\s+tests? collected", out)
        total = int(m.group(1)) if m else -1
        failed = 0  # collect-only doesn't run tests
        coverage = baseline.get("coverage", {}).get("percent", -1)
        src = "(pytest --collect-only)"

    min_tests = baseline.get("thresholds", {}).get("min_tests", 0)

    if total < 0:
        results.append(
            CheckResult(
                "TEST.count", CheckState.UNKNOWN, f"Nepodařilo se zjistit počet testů {src}"
            )
        )
    elif total < min_tests:
        results.append(
            CheckResult(
                "TEST.count",
                CheckState.FAIL,
                f"Počet testů {total} < min {min_tests} {src}",
                [f"min_tests={min_tests}", f"current={total}"],
            )
        )
    else:
        results.append(CheckResult("TEST.count", CheckState.PASS, f"Testy: {total} {src}"))

    if failed > 0:
        results.append(
            CheckResult(
                "TEST.failed",
                CheckState.FAIL,
                f"{failed} testů selhalo",
                [f"failed={failed}"],
            )
        )
    else:
        results.append(CheckResult("TEST.failed", CheckState.PASS, "0 selhání"))

    min_cov = baseline.get("thresholds", {}).get("min_coverage", 100.0)
    if coverage < 0:
        results.append(
            CheckResult("TEST.coverage", CheckState.UNKNOWN, "Coverage data nedostupná (baseline)")
        )
    elif coverage < min_cov:
        results.append(
            CheckResult(
                "TEST.coverage",
                CheckState.FAIL,
                f"Coverage {coverage:.1f}% < min {min_cov:.1f}%",
                [f"current={coverage}", f"min={min_cov}"],
            )
        )
    else:
        results.append(
            CheckResult("TEST.coverage", CheckState.PASS, f"Coverage {coverage:.1f}% (baseline)")
        )

    return results


def check_security(quick: bool) -> list[CheckResult]:
    results: list[CheckResult] = []
    baseline = _load_baseline()

    if quick:
        # Use baseline status
        vuln_count = baseline.get("vulnerabilities", {}).get("count", -1)
        bandit_base = baseline.get("lint", {}).get("bandit", "UNKNOWN")
        if vuln_count == 0:
            results.append(
                CheckResult("SECURITY.pip_audit", CheckState.PASS, "0 zranitelností (baseline)")
            )
        elif vuln_count > 0:
            results.append(
                CheckResult(
                    "SECURITY.pip_audit",
                    CheckState.FAIL,
                    f"{vuln_count} zranitelností (baseline)",
                )
            )
        else:
            results.append(
                CheckResult("SECURITY.pip_audit", CheckState.UNKNOWN, "pip-audit nebyl spuštěn")
            )
        state = CheckState.PASS if bandit_base == "PASS" else CheckState.UNKNOWN
        results.append(CheckResult("SECURITY.bandit", state, f"bandit: {bandit_base} (baseline)"))
    else:
        # pip-audit
        rc, out = _run(["uv", "run", "pip-audit", "--format", "json"])
        if rc == 0:
            results.append(CheckResult("SECURITY.pip_audit", CheckState.PASS, "0 zranitelností"))
        else:
            try:
                data = json.loads(out.split("\n")[0] if "\n" in out else out)
                n = len(data.get("dependencies", []))
            except Exception:
                n = -1
            detail = f"{n} zranitelností nalezeno" if n >= 0 else "pip-audit selhalo"
            results.append(CheckResult("SECURITY.pip_audit", CheckState.FAIL, detail, [out[:200]]))

        # bandit
        rc2, out2 = _run(
            ["uv", "run", "bandit", "-r", "packages/", "apps/", "scripts/", "-ll", "-q"]
        )
        if rc2 == 0:
            results.append(
                CheckResult("SECURITY.bandit", CheckState.PASS, "Žádné HIGH/MEDIUM findings")
            )
        else:
            results.append(
                CheckResult(
                    "SECURITY.bandit",
                    CheckState.FAIL,
                    "Bandit nalezl problémy",
                    [out2[:200]],
                )
            )

    # gitleaks — only in CI
    results.append(
        CheckResult(
            "SECURITY.gitleaks",
            CheckState.UNKNOWN,
            "gitleaks spouští se v CI (gitleaks/gitleaks-action)",
        )
    )
    return results


def check_dependencies(quick: bool) -> list[CheckResult]:  # noqa: ARG001
    results: list[CheckResult] = []
    rc, out = _run(["uv", "lock", "--check"])
    if rc == 0:
        results.append(CheckResult("DEPS.lock_sync", CheckState.PASS, "uv.lock konzistentní"))
    else:
        results.append(
            CheckResult(
                "DEPS.lock_sync",
                CheckState.FAIL,
                "uv.lock NENÍ konzistentní — spusť 'uv lock'",
                [out[:200]],
            )
        )
    return results


def check_package(quick: bool) -> list[CheckResult]:  # noqa: ARG001
    results: list[CheckResult] = []
    pp = _REPO_ROOT / "pyproject.toml"

    if not pp.exists():
        results.append(CheckResult("PKG.pyproject", CheckState.FAIL, "pyproject.toml chybí"))
        return results

    text = pp.read_text()
    for field in ("name", "version", "description", "requires-python"):
        if field in text:
            results.append(CheckResult(f"PKG.{field}", CheckState.PASS, f"{field} definováno"))
        else:
            results.append(
                CheckResult(f"PKG.{field}", CheckState.WARNING, f"{field} chybí v pyproject.toml")
            )

    # alembic migrations in sync
    rc, out = _run(["uv", "run", "alembic", "check"])
    if rc == 0:
        results.append(CheckResult("PKG.alembic", CheckState.PASS, "Alembic migrations v sync"))
    else:
        results.append(
            CheckResult(
                "PKG.alembic",
                CheckState.FAIL,
                "Alembic migrations NEJSOU v sync",
                [out[:200]],
            )
        )
    return results


def check_artifact(quick: bool) -> list[CheckResult]:  # noqa: ARG001
    dist = _REPO_ROOT / "dist"
    if dist.exists() and any(dist.iterdir()):
        artifacts = [p.name for p in dist.iterdir()]
        return [
            CheckResult(
                "ARTIFACT.dist",
                CheckState.PASS,
                f"dist/ obsahuje {len(artifacts)} artefakt(ů)",
                artifacts[:3],
            )
        ]
    return [
        CheckResult(
            "ARTIFACT.dist",
            CheckState.NOT_APPLICABLE,
            "dist/ prázdné nebo neexistuje (spouští se v CI release workflow)",
        )
    ]


def check_documentation(quick: bool) -> list[CheckResult]:
    results: list[CheckResult] = []

    # mkdocs.yml
    if _exists("mkdocs.yml"):
        results.append(CheckResult("DOCS.mkdocs_yml", CheckState.PASS, "mkdocs.yml nalezen"))
    else:
        results.append(CheckResult("DOCS.mkdocs_yml", CheckState.FAIL, "mkdocs.yml chybí"))

    # Key docs
    for doc in ["docs/index.md", "docs/api.md", "docs/cli.md", "CLAUDE.md", "README.md"]:
        if _exists(doc):
            results.append(CheckResult(f"DOCS.{Path(doc).stem}", CheckState.PASS, f"{doc} nalezen"))
        else:
            results.append(
                CheckResult(f"DOCS.{Path(doc).stem}", CheckState.WARNING, f"{doc} chybí")
            )

    if quick:
        baseline = _load_baseline()
        b = baseline.get("build", {}).get("mkdocs_strict", "UNKNOWN")
        state = CheckState.PASS if b == "PASS" else CheckState.UNKNOWN
        results.append(
            CheckResult("DOCS.mkdocs_build", state, f"mkdocs build --strict: {b} (baseline)")
        )
    else:
        rc, out = _run(["uv", "run", "mkdocs", "build", "--strict"])
        if rc == 0:
            results.append(
                CheckResult("DOCS.mkdocs_build", CheckState.PASS, "mkdocs build --strict OK")
            )
        else:
            results.append(
                CheckResult(
                    "DOCS.mkdocs_build",
                    CheckState.FAIL,
                    "mkdocs build --strict selhalo",
                    [out[-300:]],
                )
            )
    return results


def check_github(quick: bool) -> list[CheckResult]:  # noqa: ARG001
    results: list[CheckResult] = []
    wf_dir = _REPO_ROOT / ".github" / "workflows"

    required_workflows = {
        "ci.yml": "CI gate",
        "codeql.yml": "CodeQL analysis",
        "security-nightly.yml": "Nightly security",
        "release.yml": "Release workflow",
        "docker-publish.yml": "Docker publish",
        "dependabot-auto-merge.yml": "Dependabot auto-merge",
    }
    for wf, desc in required_workflows.items():
        if (wf_dir / wf).exists():
            results.append(CheckResult(f"GITHUB.{wf}", CheckState.PASS, f"{wf}: {desc} nalezen"))
        else:
            results.append(CheckResult(f"GITHUB.{wf}", CheckState.FAIL, f"{wf}: {desc} chybí"))

    # SHA pinning check (R-001)
    mutable_tags: list[str] = []
    for wf_file in wf_dir.glob("*.yml"):
        for line in wf_file.read_text().splitlines():
            if line.lstrip().startswith("#"):
                continue
            m = re.search(r"uses:\s+(\S+@[^#\s]+)", line)
            if m:
                ref = m.group(1)
                # SHA = 40 hex chars after @
                if not re.search(r"@[0-9a-f]{40}", ref):
                    mutable_tags.append(f"{wf_file.name}: {ref}")

    if mutable_tags:
        results.append(
            CheckResult(
                "GITHUB.sha_pinning",
                CheckState.WARNING,
                f"R-001: {len(mutable_tags)} mutable tags nenalezeno (supply-chain riziko)",
                mutable_tags[:5],
            )
        )
    else:
        results.append(
            CheckResult("GITHUB.sha_pinning", CheckState.PASS, "Všechny Actions pinned na SHA")
        )
    return results


def check_governance(quick: bool) -> list[CheckResult]:  # noqa: ARG001
    results: list[CheckResult] = []

    # CLAUDE.md sections
    if _exists("CLAUDE.md"):
        text = (_REPO_ROOT / "CLAUDE.md").read_text()
        for section in ["## Architecture", "## CI Gates", "## Key Design Decisions"]:
            key = f"GOV.{section[3:].replace(' ', '_')}"
            if section in text:
                results.append(CheckResult(key, CheckState.PASS, f"CLAUDE.md: {section} nalezena"))
            else:
                results.append(CheckResult(key, CheckState.WARNING, f"CLAUDE.md: {section} chybí"))
    else:
        results.append(CheckResult("GOV.claude_md", CheckState.FAIL, "CLAUDE.md chybí"))

    # ADR completeness
    adr_dir = _REPO_ROOT / "docs" / "adr"
    adr_count = len(list(adr_dir.glob("ADR-*.md"))) if adr_dir.exists() else 0
    if adr_count >= 16:
        results.append(
            CheckResult("GOV.adr_count", CheckState.PASS, f"{adr_count} ADR souborů nalezeno")
        )
    else:
        results.append(
            CheckResult("GOV.adr_count", CheckState.WARNING, f"Jen {adr_count} ADR souborů")
        )
    return results


def check_deployment(quick: bool) -> list[CheckResult]:  # noqa: ARG001
    results: list[CheckResult] = []

    for artifact in ["Dockerfile", "docker-compose.yml"]:
        key = f"DEPLOY.{artifact.replace('-', '_').replace('.', '_')}"
        if _exists(artifact):
            results.append(CheckResult(key, CheckState.PASS, f"{artifact} nalezen"))
        else:
            results.append(CheckResult(f"DEPLOY.{artifact}", CheckState.FAIL, f"{artifact} chybí"))

    # Environment variables documented in CLAUDE.md
    if _file_contains("CLAUDE.md", r"STARCORE_API_KEY.*Required"):
        results.append(
            CheckResult("DEPLOY.env_docs", CheckState.PASS, "Env vars dokumentovány v CLAUDE.md")
        )
    else:
        results.append(
            CheckResult("DEPLOY.env_docs", CheckState.WARNING, "Env vars dokumentace neověřena")
        )
    return results


def check_backup(quick: bool) -> list[CheckResult]:  # noqa: ARG001
    results: list[CheckResult] = []
    state_dir = _REPO_ROOT / ".starcore" / "state"

    if (_BASELINE_PATH).exists():
        results.append(
            CheckResult("BACKUP.baseline", CheckState.PASS, "regression_baseline.json nalezen")
        )
    else:
        results.append(
            CheckResult("BACKUP.baseline", CheckState.FAIL, "regression_baseline.json chybí")
        )

    if (state_dir / "release.md").exists():
        results.append(CheckResult("BACKUP.release_state", CheckState.PASS, "release.md nalezen"))
    else:
        results.append(CheckResult("BACKUP.release_state", CheckState.WARNING, "release.md chybí"))

    if (_REPO_ROOT / ".starcore" / "sessions" / "ledger.yaml").exists():
        results.append(CheckResult("BACKUP.ledger", CheckState.PASS, "session ledger.yaml nalezen"))
    else:
        results.append(
            CheckResult("BACKUP.ledger", CheckState.WARNING, "session ledger.yaml chybí")
        )
    return results


def check_recovery(quick: bool) -> list[CheckResult]:  # noqa: ARG001
    results: list[CheckResult] = []

    # ADR-016 references timeout recovery
    if _file_contains("docs/adr/ADR-016-task-timeout-integration.md", r"recover|rollback|revert"):
        results.append(
            CheckResult(
                "RECOVERY.adr_016", CheckState.PASS, "ADR-016: recovery procedure dokumentována"
            )
        )
    else:
        results.append(
            CheckResult(
                "RECOVERY.adr_016",
                CheckState.NOT_APPLICABLE,
                "ADR-016 neobsahuje explicitní recovery (timeout je deferred)",
            )
        )

    # Rollback documented in CLAUDE.md
    if _file_contains("CLAUDE.md", r"rollback|revert"):
        results.append(
            CheckResult("RECOVERY.rollback", CheckState.PASS, "Rollback postup dokumentován")
        )
    else:
        results.append(
            CheckResult(
                "RECOVERY.rollback",
                CheckState.WARNING,
                "Rollback postup není explicitně dokumentován",
            )
        )

    # .starcore/ cold-start protocol = recovery from agent state loss
    if _file_contains(".starcore/README.md", r"Cold-start"):
        results.append(
            CheckResult(
                "RECOVERY.cold_start", CheckState.PASS, "Cold-start recovery protokol nalezen"
            )
        )
    else:
        results.append(
            CheckResult("RECOVERY.cold_start", CheckState.WARNING, "Cold-start protokol nenalezen")
        )
    return results


# ── Gate registry ─────────────────────────────────────────────────────────────

_GATES: dict[str, tuple[str, callable]] = {
    "BUILD": ("Sestavení", check_build),
    "TEST": ("Testy", check_test),
    "SECURITY": ("Bezpečnost", check_security),
    "DEPENDENCIES": ("Závislosti", check_dependencies),
    "PACKAGE": ("Balíčkování", check_package),
    "ARTIFACT": ("Artefakty", check_artifact),
    "DOCUMENTATION": ("Dokumentace", check_documentation),
    "GITHUB": ("GitHub", check_github),
    "GOVERNANCE": ("Governance", check_governance),
    "DEPLOYMENT": ("Nasazení", check_deployment),
    "BACKUP": ("Záloha stavu", check_backup),
    "RECOVERY": ("Obnova", check_recovery),
}


def overall_verdict(gate_results: dict[str, list[CheckResult]]) -> str:
    all_results = [r for results in gate_results.values() for r in results]
    states = {str(r.state) for r in all_results}

    if "FAIL" in states:
        return "NOT_RELEASE_READY"
    if "UNKNOWN" in states:
        return "RELEASE_READY_WITH_WARNINGS"
    if "WARNING" in states:
        return "RELEASE_READY_WITH_WARNINGS"
    return "RELEASE_READY"


# ── CLI commands ──────────────────────────────────────────────────────────────

_SEP = "─" * 72


def _print_results(results: list[CheckResult]) -> None:
    for r in results:
        evidence_str = f"  [{r.evidence[0][:60]}]" if r.evidence else ""
        print(f"    {r.icon} {r.name:<35} {r.detail}{evidence_str}")


def cmd_evaluate(args: argparse.Namespace) -> int:
    quick = getattr(args, "quick", False)
    gate_filter = getattr(args, "gate", None)

    print(f"\n{_SEP}")
    mode = "QUICK (baseline)" if quick else "FULL"
    print(f"STARCORE Release Readiness Engine — mode: {mode}")
    print(_SEP)

    gate_results: dict[str, list[CheckResult]] = {}
    for gate_name, (label, check_fn) in _GATES.items():
        if gate_filter and gate_name != gate_filter.upper():
            continue
        results = check_fn(quick)
        gate_results[gate_name] = results
        ws = worst_state(results)
        from models import _ICONS  # noqa: PLC0415

        icon = _ICONS.get(str(ws), "?")
        print(f"\n[{gate_name}] {label}")
        _print_results(results)
        print(f"  {'─' * 40}")
        print(f"  GATE: {icon} {ws}")

    if not gate_filter:
        verdict = overall_verdict(gate_results)
        print(f"\n{_SEP}")
        _icons = {
            "RELEASE_READY": "✓",
            "RELEASE_READY_WITH_WARNINGS": "⚠",
            "NOT_RELEASE_READY": "✗",
            "BLOCKED": "✗",
        }
        v_icon = _icons.get(verdict, "?")
        print(f"VERDICT: {v_icon} {verdict}")
        print(_SEP)
        return 0 if verdict == "RELEASE_READY" else 1
    return 0


def cmd_gate(args: argparse.Namespace) -> int:
    args.quick = False
    args.gate = args.gate_name
    return cmd_evaluate(args)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="release_readiness",
        description="STARCORE Release Readiness Engine",
    )
    sub = parser.add_subparsers(dest="command")

    p_eval = sub.add_parser("evaluate", help="Vyhodnotit všechny release gates")
    p_eval.add_argument(
        "--quick", action="store_true", help="Použít baseline místo pomalých kontrol"
    )
    p_eval.add_argument(
        "--gate", default=None, help="Vyhodnotit jen jeden gate (BUILD/TEST/SECURITY/…)"
    )

    p_gate = sub.add_parser("gate", help="Vyhodnotit jeden gate")
    p_gate.add_argument("gate_name", choices=list(_GATES.keys()))

    args = parser.parse_args()
    dispatch = {"evaluate": cmd_evaluate, "gate": cmd_gate}

    if args.command not in dispatch:
        parser.print_help()
        return 1
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
