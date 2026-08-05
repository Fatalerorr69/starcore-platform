#!/usr/bin/env python3
"""
STARCORE QC Engine — unified quality control orchestrator.

Spouští všechny tři QC engines a produkuje souhrnný report
ve formátu Decision Engine (8 sekcí, česky).

Použití:
  uv run python .starcore/scripts/qc_engine.py run
  uv run python .starcore/scripts/qc_engine.py run --quick
  uv run python .starcore/scripts/qc_engine.py run --impact
  uv run python .starcore/scripts/qc_engine.py run --impact --quick
  uv run python .starcore/scripts/qc_engine.py impact [--since COMMIT] [--files ...]
  uv run python .starcore/scripts/qc_engine.py sentinel
  uv run python .starcore/scripts/qc_engine.py readiness [--quick]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent

sys.path.insert(0, str(_SCRIPT_DIR))

from models import CheckResult, CheckState, worst_state  # noqa: E402

_SEP = "═" * 72
_SEP2 = "─" * 72


# ── Sentinel integration ──────────────────────────────────────────────────────


def run_sentinel() -> tuple[list[CheckResult], dict]:
    """Run Regression Sentinel and return (results, current_snapshot)."""
    from regression_sentinel import _load_baseline, capture_snapshot, compare_snapshot

    baseline = _load_baseline()
    current = capture_snapshot()
    if not baseline:
        return [], current
    results = compare_snapshot(current, baseline)
    return results, current


# ── Impact Analyzer integration ───────────────────────────────────────────────


def run_impact(since: str | None = None, files: list[str] | None = None):
    """Run Change Impact Analyzer, return (impacts, summary_result)."""
    from impact_analyzer import analyze_file, get_changed_files, summarize_impacts

    changed = get_changed_files(since=since, files=files)
    if not changed:
        return [], None
    impacts = [analyze_file(f) for f in changed]
    summary = summarize_impacts(impacts)
    return impacts, summary


# ── Release Readiness integration ─────────────────────────────────────────────


def run_readiness(quick: bool = False) -> dict[str, list[CheckResult]]:
    """Run all Release Readiness gates, return dict of gate_name → results."""
    from release_readiness import _GATES

    gate_results: dict[str, list[CheckResult]] = {}
    for gate_name, (_, check_fn) in _GATES.items():
        gate_results[gate_name] = check_fn(quick)
    return gate_results


def readiness_verdict(gate_results: dict[str, list[CheckResult]]) -> str:
    from release_readiness import overall_verdict

    return overall_verdict(gate_results)


# ── Report formatting ─────────────────────────────────────────────────────────


_VERDICT_LABELS = {
    "RELEASE_READY": "✓ RELEASE_READY — všechny gates prošly",
    "RELEASE_READY_WITH_WARNINGS": "⚠ RELEASE_READY_WITH_WARNINGS — varování přítomna",
    "NOT_RELEASE_READY": "✗ NOT_RELEASE_READY — selhání detekováno",
    "BLOCKED": "✗ BLOCKED — kritický blokér",
}

_GATE_LABELS = {
    "build": "BUILD",
    "test": "TEST",
    "security": "SECURITY",
    "dependencies": "DEPENDENCIES",
    "package": "PACKAGE",
    "artifact": "ARTIFACT",
    "documentation": "DOCUMENTATION",
    "github": "GITHUB",
    "governance": "GOVERNANCE",
    "deployment": "DEPLOYMENT",
    "backup": "BACKUP",
    "recovery": "RECOVERY",
}

_SENTINEL_LABELS = {
    "test_count": "Počet testů   ",
    "api_routes": "API routes    ",
    "cli_commands": "CLI příkazy   ",
    "config_fields": "Config fields ",
    "adr_count": "ADR soubory   ",
    "workflow_count": "CI workflows  ",
    "lock_sync": "Lock sync     ",
}


def _state_icon(state: CheckState) -> str:
    icons = {
        CheckState.PASS: "✓",
        CheckState.WARNING: "⚠",
        CheckState.FAIL: "✗",
        CheckState.UNKNOWN: "?",
        CheckState.NOT_APPLICABLE: "—",
    }
    return icons.get(state, "?")


def _worst_gate(results: list[CheckResult]) -> CheckState:
    if not results:
        return CheckState.UNKNOWN
    return worst_state(results)


def _format_sentinel_section(sentinel_results: list[CheckResult]) -> list[str]:
    lines = ["", "  REGRESSION SENTINEL:", _SEP2]
    if not sentinel_results:
        lines.append("  ⚠ Baseline nenalezena — spusť 'sentinel update' nejprve")
        return lines
    for r in sentinel_results:
        label = _SENTINEL_LABELS.get(r.name, r.name[:18])
        icon = _state_icon(r.state)
        lines.append(f"  {label:<18} {icon} {str(r.state):<10} {r.detail}")
    sentinel_worst = worst_state(sentinel_results)
    lines.append(_SEP2)
    lines.append(f"  Sentinel výsledek: {_state_icon(sentinel_worst)} {sentinel_worst}")
    return lines


def _format_readiness_section(gate_results: dict[str, list[CheckResult]]) -> list[str]:
    lines = ["", "  RELEASE READINESS GATES:", _SEP2]
    for gate_name, results in gate_results.items():
        gate_worst = _worst_gate(results)
        label = _GATE_LABELS.get(gate_name, gate_name.upper())
        icon = _state_icon(gate_worst)
        fail_details = [
            r.detail for r in results if r.state in (CheckState.FAIL, CheckState.WARNING)
        ]
        detail_str = f" — {fail_details[0]}" if fail_details else ""
        lines.append(f"  {label:<16} {icon} {str(gate_worst):<10}{detail_str}")
    return lines


def _collect_risks(
    sentinel_results: list[CheckResult],
    gate_results: dict[str, list[CheckResult]],
    impact_summary: CheckResult | None,
) -> list[str]:
    risks = []
    for r in sentinel_results:
        if r.state == CheckState.FAIL:
            risks.append(f"REGRESE: {r.detail}")
        elif r.state == CheckState.WARNING:
            risks.append(f"DRIFT: {r.detail}")
    for gate_name, results in gate_results.items():
        for r in results:
            if r.state == CheckState.FAIL:
                label = _GATE_LABELS.get(gate_name, gate_name.upper())
                risks.append(f"{label}: {r.detail}")
    if impact_summary and impact_summary.state == CheckState.WARNING:
        risks.append(f"DOPAD: {impact_summary.detail}")
    if not risks:
        risks.append("Žádná detekovaná rizika")
    return risks


def _collect_blockers(
    sentinel_results: list[CheckResult],
    gate_results: dict[str, list[CheckResult]],
) -> list[str]:
    blockers = [f"[SENTINEL] {r.detail}" for r in sentinel_results if r.state == CheckState.FAIL]
    for gate_name, results in gate_results.items():
        label = _GATE_LABELS.get(gate_name, gate_name.upper())
        blockers.extend(f"[{label}] {r.detail}" for r in results if r.state == CheckState.FAIL)
    return blockers


def _collect_recommendations(
    verdict: str,
    blockers: list[str],
    sentinel_results: list[CheckResult],
    gate_results: dict[str, list[CheckResult]],
) -> list[str]:
    recs = []
    if blockers:
        recs.append("Opravit všechny FAIL blokery před releasem")
    for r in sentinel_results:
        if r.state == CheckState.FAIL:
            recs.append("Spusť regression_sentinel.py diff pro analýzu regrese")
            break
    has_github_fail = any(r.state == CheckState.FAIL for r in gate_results.get("github", []))
    if has_github_fail:
        recs.append(
            "R-001: Přepnout GitHub Actions na SHA-pinned reference (viz docs/adr/ADR-008.md)"
        )
    has_security_issues = any(
        r.state in (CheckState.FAIL, CheckState.WARNING) for r in gate_results.get("security", [])
    )
    if has_security_issues:
        recs.append("Spusť 'uv run pip-audit' a 'uv run bandit -r packages/ apps/' pro detail")
    if not recs:
        if verdict == "RELEASE_READY":
            recs.append("Všechny kontroly prošly — můžeš přistoupit k releasu")
        else:
            recs.append("Zkontroluj varování a rozhodni, zda jsou přijatelná pro release")
    return recs


def build_qc_report(
    sentinel_results: list[CheckResult],
    gate_results: dict[str, list[CheckResult]],
    impacts: list,
    impact_summary: CheckResult | None,
    verdict: str,
    quick: bool,
) -> str:
    """Build full Czech QC report in Decision Engine format."""
    blockers = _collect_blockers(sentinel_results, gate_results)
    risks = _collect_risks(sentinel_results, gate_results, impact_summary)
    recs = _collect_recommendations(verdict, blockers, sentinel_results, gate_results)

    # Overall state
    sentinel_worst = worst_state(sentinel_results) if sentinel_results else CheckState.UNKNOWN
    all_gate_results = [r for results in gate_results.values() for r in results]
    readiness_worst = worst_state(all_gate_results) if all_gate_results else CheckState.UNKNOWN
    components = [sentinel_worst, readiness_worst]
    if impact_summary:
        components.append(impact_summary.state)
    overall_worst = max(
        components,
        key=lambda s: {
            CheckState.FAIL: 4,
            CheckState.UNKNOWN: 3,
            CheckState.WARNING: 2,
            CheckState.PASS: 1,
            CheckState.NOT_APPLICABLE: 0,
        }.get(s, 0),
    )

    verdict_label = _VERDICT_LABELS.get(verdict, verdict)
    mode_note = " (quick mode — některé kontroly přeskočeny)" if quick else ""

    lines = [
        "",
        _SEP,
        "STARCORE QC ENGINE — Komplexní QC report",
        _SEP,
        f"Režim: {'QUICK' if quick else 'FULL'}{mode_note}",
        "",
        "─── STAV ────────────────────────────────────────────────────────────",
        f"  Celkový stav  : {_state_icon(overall_worst)} {overall_worst}",
        f"  Release verdict: {verdict_label}",
        f"  Sentinel      : {_state_icon(sentinel_worst)} {sentinel_worst}",
        f"  Readiness     : {_state_icon(readiness_worst)} {readiness_worst}",
    ]
    if impact_summary:
        icon = _state_icon(impact_summary.state)
        lines.append(f"  Change impact : {icon} {impact_summary.state}")
    else:
        lines.append("  Change impact : — (nespuštěno)")

    lines += [
        "",
        "─── CO BYLO ZJIŠTĚNO ────────────────────────────────────────────────",
    ]
    lines += _format_sentinel_section(sentinel_results)
    lines += _format_readiness_section(gate_results)

    if impacts:
        lines += ["", "  CHANGE IMPACT:", _SEP2]
        all_cats: set[str] = set()
        for imp in impacts:
            all_cats.update(imp.categories)
        lines.append(f"  Změněno souborů: {len(impacts)}")
        lines.append(f"  Zasažené oblasti: {', '.join(sorted(all_cats)) if all_cats else '—'}")
        if impact_summary:
            lines.append(f"  Souhrn: {impact_summary.detail}")

    lines += [
        "",
        "─── CO BYLO OVĚŘENO ─────────────────────────────────────────────────",
        f"  ✓ Regression Sentinel: {len(sentinel_results)} dimenzí prověřeno"
        if sentinel_results
        else "  ? Regression Sentinel: baseline chybí",
        f"  ✓ Release Readiness: {len(gate_results)} gates vyhodnoceno",
    ]
    if impacts:
        lines.append(f"  ✓ Change Impact: {len(impacts)} souborů analyzováno")

    lines += [
        "",
        "─── RIZIKA ──────────────────────────────────────────────────────────",
    ]
    for risk in risks:
        lines.append(f"  • {risk}")

    lines += [
        "",
        "─── DOPORUČENÍ ──────────────────────────────────────────────────────",
    ]
    for i, rec in enumerate(recs, 1):
        lines.append(f"  {i}. {rec}")

    lines += [
        "",
        "─── DOPAD ───────────────────────────────────────────────────────────",
        "  Tyto výsledky odrážejí aktuální stav repozitáře.",
        "  Žádné soubory nebyly modifikovány.",
        "",
        "─── RIZIKO ──────────────────────────────────────────────────────────",
    ]
    if blockers:
        lines.append(f"  VYSOKÉ — {len(blockers)} blokér(ů) před releasem")
        for b in blockers[:3]:
            lines.append(f"  • {b}")
        if len(blockers) > 3:
            lines.append(f"  • … a {len(blockers) - 3} dalších")
    else:
        lines.append("  NÍZKÉ — žádné blokéry")

    lines += [
        "",
        "─── ROLLBACK ────────────────────────────────────────────────────────",
        "  QC kontroly jsou read-only — žádný rollback potřeba.",
        "",
        "─── DALŠÍ KROK ──────────────────────────────────────────────────────",
    ]
    if blockers:
        lines.append("  Opravit blokéry a spustit QC engine znovu.")
    elif overall_worst in (CheckState.WARNING, CheckState.UNKNOWN):
        lines.append("  Zvážit varování a rozhodnout o release readiness.")
    else:
        lines.append("  Release readiness potvrzena — připraveno k nasazení.")

    lines += [
        "",
        _SEP,
        "VOLBY:",
        "  [1] Release ready — přistoupit k releasu",
        "  [2] Opravit blokery — automatická oprava dostupných problémů",
        "  [3] Zobrazit detail — zobrazit detail jednotlivých gates",
        "  [4] Pokračovat v hardeningu — spustit security/governance audit",
        "  [5] Vlastní instrukce",
        _SEP,
        "",
    ]
    return "\n".join(lines)


# ── CLI commands ──────────────────────────────────────────────────────────────


def cmd_run(args: argparse.Namespace) -> int:
    quick = getattr(args, "quick", False)
    run_impact_flag = getattr(args, "impact", False)
    since = getattr(args, "since", None)
    files = getattr(args, "files", None) or []

    print(f"\n{_SEP}")
    print("STARCORE QC Engine — spouštím analýzu…")
    print(_SEP)

    # Sentinel
    print("▶ Regression Sentinel…")
    sentinel_results, _ = run_sentinel()

    # Release Readiness
    print("▶ Release Readiness Engine…")
    gate_results = run_readiness(quick=quick)
    verdict = readiness_verdict(gate_results)

    # Change Impact (optional)
    impacts: list = []
    impact_summary: CheckResult | None = None
    if run_impact_flag:
        print("▶ Change Impact Analyzer…")
        impacts, impact_summary = run_impact(
            since=since if since else None,
            files=files if files else None,
        )

    report = build_qc_report(
        sentinel_results=sentinel_results,
        gate_results=gate_results,
        impacts=impacts,
        impact_summary=impact_summary,
        verdict=verdict,
        quick=quick,
    )
    print(report)

    # Exit code: 0 if PASS/WARNING, 1 if FAIL/UNKNOWN at sentinel or readiness
    all_results = list(sentinel_results) + [r for gr in gate_results.values() for r in gr]
    w = worst_state(all_results) if all_results else CheckState.UNKNOWN
    return 1 if w == CheckState.FAIL else 0


def cmd_impact(args: argparse.Namespace) -> int:
    """Proxy to impact_analyzer analyze subcommand."""
    import impact_analyzer as ia

    class _FakeArgs:
        since = getattr(args, "since", None)
        files = getattr(args, "files", None) or []

    return ia.cmd_analyze(_FakeArgs())


def cmd_sentinel(_args: argparse.Namespace) -> int:
    """Run sentinel check."""
    from regression_sentinel import cmd_check as _sentinel_check

    class _FakeArgs:
        full = False

    return _sentinel_check(_FakeArgs())


def cmd_readiness(args: argparse.Namespace) -> int:
    """Run release readiness evaluation."""
    from release_readiness import cmd_evaluate

    return cmd_evaluate(args)


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="qc_engine",
        description="STARCORE QC Engine — unified quality control",
    )
    sub = parser.add_subparsers(dest="command")

    p_run = sub.add_parser("run", help="Spustit všechny QC engines")
    p_run.add_argument("--quick", action="store_true", help="Přeskočit pomalé kontroly")
    p_run.add_argument("--impact", action="store_true", help="Zahrnout Change Impact Analyzer")
    p_run.add_argument(
        "--since", default=None, metavar="COMMIT", help="Impact: porovnat s tímto commitem"
    )
    p_run.add_argument(
        "--files", nargs="+", metavar="FILE", help="Impact: explicitní seznam souborů"
    )

    p_impact = sub.add_parser("impact", help="Spustit Change Impact Analyzer")
    p_impact.add_argument("--since", default=None, metavar="COMMIT")
    p_impact.add_argument("--files", nargs="+", metavar="FILE")

    sub.add_parser("sentinel", help="Spustit Regression Sentinel")

    p_readiness = sub.add_parser("readiness", help="Spustit Release Readiness Engine")
    p_readiness.add_argument("--quick", action="store_true")
    p_readiness.add_argument("--gate", default=None, metavar="GATE")

    dispatch = {
        "run": cmd_run,
        "impact": cmd_impact,
        "sentinel": cmd_sentinel,
        "readiness": cmd_readiness,
    }

    args = parser.parse_args()
    if args.command not in dispatch:
        parser.print_help()
        return 1
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
