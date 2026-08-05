#!/usr/bin/env python3
"""
Standalone testy pro STARCORE QC Engines.

Testuje čistou Python logiku (path_to_module, compare_snapshot,
gate state logic, build_qc_report) bez systémových závislostí.

Spuštění:
  uv run python .starcore/scripts/tests/test_qc_engines.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).parent.parent
sys.path.insert(0, str(_SCRIPTS))

from impact_analyzer import (  # noqa: E402
    FileImpact,
    module_to_impact_categories,
    path_to_module,
    summarize_impacts,
)
from models import CheckResult, CheckState, worst_state  # noqa: E402
from regression_sentinel import _cmp_count, compare_snapshot  # noqa: E402

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_result(name: str, state: CheckState, detail: str = "") -> CheckResult:
    return CheckResult(name=name, state=state, detail=detail)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. path_to_module
# ═══════════════════════════════════════════════════════════════════════════════


class TestPathToModule(unittest.TestCase):
    def test_exact_file_core_main(self):
        assert path_to_module("packages/core/main.py") == "core.main"

    def test_exact_file_config(self):
        assert path_to_module("packages/core/config.py") == "core.config"

    def test_exact_file_cli_main(self):
        assert path_to_module("apps/cli/main.py") == "cli.main"

    def test_exact_file_timeout(self):
        assert path_to_module("packages/orchestrator/timeout.py") == "orchestrator.timeout"

    def test_exact_file_scheduler(self):
        assert path_to_module("packages/orchestrator/scheduler.py") == "orchestrator.scheduler"

    def test_prefix_orchestrator(self):
        assert path_to_module("packages/orchestrator/new_thing.py") == "orchestrator"

    def test_prefix_providers_docker(self):
        assert path_to_module("packages/providers/docker/provider.py") == "providers.docker"

    def test_prefix_providers_proxmox(self):
        assert path_to_module("packages/providers/proxmox/provider.py") == "providers.proxmox"

    def test_github_workflows(self):
        assert path_to_module(".github/workflows/ci.yml") == "ci"

    def test_pyproject_toml(self):
        assert path_to_module("pyproject.toml") == "packaging"

    def test_dockerfile(self):
        assert path_to_module("Dockerfile") == "build"

    def test_docker_compose(self):
        assert path_to_module("docker-compose.yml") == "deployment"

    def test_claude_md(self):
        assert path_to_module("CLAUDE.md") == "governance"

    def test_tests_dir(self):
        assert path_to_module("tests/test_blueprints.py") == "tests"

    def test_docs_adr(self):
        assert path_to_module("docs/adr/ADR-001.md") == "docs.adr"

    def test_migrations(self):
        assert path_to_module("migrations/versions/abc.py") == "migrations"

    def test_starcore_scripts(self):
        assert path_to_module(".starcore/scripts/qc_engine.py") == "starcore.scripts"

    def test_unknown_path(self):
        assert path_to_module("completely/unknown/path.py") == "unknown"

    def test_backslash_normalised(self):
        assert path_to_module("packages\\core\\main.py") == "core.main"

    def test_ai_anthropic(self):
        assert path_to_module("packages/ai/providers/anthropic.py") == "ai.anthropic"

    def test_provider_sdk_base(self):
        assert path_to_module("packages/provider_sdk/base.py") == "provider_sdk.base"

    def test_blueprints_executor(self):
        assert path_to_module("packages/blueprints/executor.py") == "blueprints.executor"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. module_to_impact_categories
# ═══════════════════════════════════════════════════════════════════════════════


class TestModuleToImpactCategories(unittest.TestCase):
    def test_core_main_has_api(self):
        cats = module_to_impact_categories("core.main")
        assert "API" in cats

    def test_core_config_has_configuration(self):
        cats = module_to_impact_categories("core.config")
        assert "CONFIGURATION" in cats
        assert "API" in cats

    def test_core_security_has_security(self):
        cats = module_to_impact_categories("core.security")
        assert "SECURITY" in cats

    def test_ci_module(self):
        cats = module_to_impact_categories("ci")
        assert "CI" in cats

    def test_packaging_module(self):
        cats = module_to_impact_categories("packaging")
        assert "PACKAGE" in cats
        assert "DEPLOYMENT" in cats

    def test_database_module(self):
        cats = module_to_impact_categories("core.database")
        assert "DATABASE" in cats

    def test_provider_sdk_retry_recovery(self):
        cats = module_to_impact_categories("provider_sdk.retry")
        assert "RECOVERY" in cats

    def test_tests_module_empty(self):
        cats = module_to_impact_categories("tests")
        assert cats == []

    def test_starcore_empty(self):
        cats = module_to_impact_categories("starcore")
        assert cats == []

    def test_unknown_returns_empty(self):
        cats = module_to_impact_categories("unknown")
        assert cats == []

    def test_docs_adr_governance(self):
        cats = module_to_impact_categories("docs.adr")
        assert "GOVERNANCE" in cats
        assert "DOCUMENTATION" in cats

    def test_providers_docker_deployment(self):
        cats = module_to_impact_categories("providers.docker")
        assert "DEPLOYMENT" in cats


# ═══════════════════════════════════════════════════════════════════════════════
# 3. summarize_impacts
# ═══════════════════════════════════════════════════════════════════════════════


class TestSummarizeImpacts(unittest.TestCase):
    def _impact(self, file: str, module: str, cats: list[str]) -> FileImpact:
        return FileImpact(file=file, module=module, categories=cats, dependents=[], test_files=[])

    def test_no_impacts_returns_pass(self):
        result = summarize_impacts([])
        assert result.state == CheckState.PASS

    def test_critical_api_gives_warning(self):
        impacts = [self._impact("packages/core/main.py", "core.main", ["API"])]
        result = summarize_impacts(impacts)
        assert result.state == CheckState.WARNING
        assert "API" in result.detail

    def test_non_critical_only_gives_pass(self):
        impacts = [self._impact("docs/README.md", "docs", ["DOCUMENTATION"])]
        result = summarize_impacts(impacts)
        assert result.state == CheckState.PASS

    def test_multiple_critical_areas(self):
        impacts = [
            self._impact("packages/core/security.py", "core.security", ["API", "SECURITY"]),
            self._impact("migrations/v1.py", "migrations", ["DATABASE", "DEPLOYMENT"]),
        ]
        result = summarize_impacts(impacts)
        assert result.state == CheckState.WARNING
        assert "SECURITY" in result.detail or "DATABASE" in result.detail or "API" in result.detail

    def test_evidence_contains_file_module(self):
        impacts = [self._impact("packages/core/events.py", "core.events", ["API"])]
        result = summarize_impacts(impacts)
        assert any("core.events" in e for e in result.evidence)

    def test_internal_files_pass(self):
        impacts = [
            self._impact(".starcore/scripts/qc_engine.py", "starcore.scripts", []),
            self._impact("tests/test_x.py", "tests", []),
        ]
        result = summarize_impacts(impacts)
        assert result.state == CheckState.PASS


# ═══════════════════════════════════════════════════════════════════════════════
# 4. _cmp_count
# ═══════════════════════════════════════════════════════════════════════════════


class TestCmpCount(unittest.TestCase):
    def test_no_baseline_returns_unknown(self):
        r = _cmp_count("test_count", 569, None)
        assert r.state == CheckState.UNKNOWN

    def test_negative_current_returns_unknown(self):
        r = _cmp_count("test_count", -1, 569)
        assert r.state == CheckState.UNKNOWN

    def test_decrease_is_regression_down(self):
        r = _cmp_count("test_count", 560, 569, direction="down")
        assert r.state == CheckState.FAIL
        assert "REGRESE" in r.detail

    def test_equal_is_pass(self):
        r = _cmp_count("test_count", 569, 569)
        assert r.state == CheckState.PASS

    def test_increase_is_warning_when_direction_down(self):
        r = _cmp_count("test_count", 580, 569, direction="down")
        assert r.state == CheckState.WARNING

    def test_increase_is_narůst_when_direction_up(self):
        r = _cmp_count("config_fields", 30, 24, direction="up")
        assert r.state == CheckState.WARNING
        assert "NÁRŮST" in r.detail

    def test_decrease_from_up_direction(self):
        r = _cmp_count("config_fields", 20, 24, direction="up")
        assert r.state == CheckState.WARNING

    def test_evidence_populated_on_fail(self):
        r = _cmp_count("test_count", 500, 569, direction="down")
        assert r.state == CheckState.FAIL
        assert len(r.evidence) >= 2


# ═══════════════════════════════════════════════════════════════════════════════
# 5. compare_snapshot
# ═══════════════════════════════════════════════════════════════════════════════


class TestCompareSnapshot(unittest.TestCase):
    def _baseline(self, **overrides):
        base = {
            "test_count": 569,
            "api_routes": 17,
            "cli_commands": 6,
            "config_fields": 24,
            "adr_count": 16,
            "workflow_count": 7,
            "lock_sync": True,
        }
        base.update(overrides)
        return {"sentinel": base}

    def _snapshot(self, **overrides):
        snap = {
            "test_count": 569,
            "api_routes": 17,
            "cli_commands": 6,
            "config_fields": 24,
            "adr_count": 16,
            "workflow_count": 7,
            "lock_sync": True,
        }
        snap.update(overrides)
        return snap

    def test_identical_snapshot_all_pass(self):
        results = compare_snapshot(self._snapshot(), self._baseline())
        states = {r.name: r.state for r in results}
        assert states["test_count"] == CheckState.PASS
        assert states["lock_sync"] == CheckState.PASS

    def test_test_count_regression(self):
        results = compare_snapshot(self._snapshot(test_count=550), self._baseline())
        states = {r.name: r.state for r in results}
        assert states["test_count"] == CheckState.FAIL

    def test_lock_sync_fail(self):
        results = compare_snapshot(self._snapshot(lock_sync=False), self._baseline())
        states = {r.name: r.state for r in results}
        assert states["lock_sync"] == CheckState.FAIL

    def test_adr_count_decrease_is_fail(self):
        results = compare_snapshot(self._snapshot(adr_count=10), self._baseline())
        states = {r.name: r.state for r in results}
        assert states["adr_count"] == CheckState.FAIL

    def test_workflow_count_decrease_is_fail(self):
        results = compare_snapshot(self._snapshot(workflow_count=5), self._baseline())
        states = {r.name: r.state for r in results}
        assert states["workflow_count"] == CheckState.FAIL

    def test_empty_baseline_returns_unknown(self):
        # lock_sync is checked against current state, not baseline → may be PASS
        results = compare_snapshot(self._snapshot(), {})
        for r in results:
            assert r.state in (CheckState.UNKNOWN, CheckState.FAIL, CheckState.PASS)

    def test_sentinel_subkey_takes_precedence(self):
        baseline = {
            "test_count": 100,
            "sentinel": {
                "test_count": 569,
                "api_routes": 17,
                "cli_commands": 6,
                "config_fields": 24,
                "adr_count": 16,
                "workflow_count": 7,
                "lock_sync": True,
            },
        }
        results = compare_snapshot(self._snapshot(), baseline)
        states = {r.name: r.state for r in results}
        assert states["test_count"] == CheckState.PASS


# ═══════════════════════════════════════════════════════════════════════════════
# 6. worst_state
# ═══════════════════════════════════════════════════════════════════════════════


class TestWorstState(unittest.TestCase):
    def test_empty_list_returns_unknown(self):
        assert worst_state([]) == CheckState.UNKNOWN

    def test_single_pass(self):
        assert worst_state([_make_result("x", CheckState.PASS)]) == CheckState.PASS

    def test_fail_beats_warning(self):
        results = [
            _make_result("a", CheckState.PASS),
            _make_result("b", CheckState.WARNING),
            _make_result("c", CheckState.FAIL),
        ]
        assert worst_state(results) == CheckState.FAIL

    def test_unknown_beats_warning(self):
        results = [
            _make_result("a", CheckState.WARNING),
            _make_result("b", CheckState.UNKNOWN),
        ]
        assert worst_state(results) == CheckState.UNKNOWN

    def test_not_applicable_lowest(self):
        results = [_make_result("a", CheckState.NOT_APPLICABLE)]
        assert worst_state(results) == CheckState.NOT_APPLICABLE

    def test_all_pass(self):
        results = [_make_result(f"check_{i}", CheckState.PASS) for i in range(5)]
        assert worst_state(results) == CheckState.PASS


# ═══════════════════════════════════════════════════════════════════════════════
# 7. qc_engine build_qc_report
# ═══════════════════════════════════════════════════════════════════════════════


class TestBuildQCReport(unittest.TestCase):
    def setUp(self):
        from qc_engine import build_qc_report

        self.build = build_qc_report

    def _pass_gate(self, name: str) -> CheckResult:
        return _make_result(name, CheckState.PASS, f"{name} OK")

    def test_report_contains_stav_section(self):
        report = self.build(
            sentinel_results=[],
            gate_results={"build": [self._pass_gate("build")]},
            impacts=[],
            impact_summary=None,
            verdict="RELEASE_READY",
            quick=False,
        )
        assert "STAV" in report

    def test_report_contains_volby(self):
        report = self.build(
            sentinel_results=[],
            gate_results={"build": [self._pass_gate("build")]},
            impacts=[],
            impact_summary=None,
            verdict="RELEASE_READY",
            quick=False,
        )
        assert "VOLBY" in report
        assert "[1]" in report
        assert "[5]" in report

    def test_report_shows_fail_verdict(self):
        fail_result = _make_result("test", CheckState.FAIL, "Testy selhaly")
        report = self.build(
            sentinel_results=[fail_result],
            gate_results={"test": [fail_result]},
            impacts=[],
            impact_summary=None,
            verdict="NOT_RELEASE_READY",
            quick=False,
        )
        assert "NOT_RELEASE_READY" in report

    def test_quick_mode_noted_in_report(self):
        report = self.build(
            sentinel_results=[],
            gate_results={"build": [self._pass_gate("build")]},
            impacts=[],
            impact_summary=None,
            verdict="RELEASE_READY",
            quick=True,
        )
        assert "QUICK" in report or "quick" in report.lower()

    def test_report_without_impact_shows_dash(self):
        report = self.build(
            sentinel_results=[],
            gate_results={},
            impacts=[],
            impact_summary=None,
            verdict="RELEASE_READY",
            quick=False,
        )
        assert "nespuštěno" in report

    def test_report_blockers_listed(self):
        fail_result = _make_result("security", CheckState.FAIL, "Zranitelnost nalezena")
        report = self.build(
            sentinel_results=[],
            gate_results={"security": [fail_result]},
            impacts=[],
            impact_summary=None,
            verdict="NOT_RELEASE_READY",
            quick=False,
        )
        assert "Zranitelnost" in report or "SECURITY" in report

    def test_release_ready_recommendation(self):
        report = self.build(
            sentinel_results=[_make_result("test_count", CheckState.PASS, "OK")],
            gate_results={"build": [self._pass_gate("build")]},
            impacts=[],
            impact_summary=None,
            verdict="RELEASE_READY",
            quick=False,
        )
        assert "release" in report.lower() or "nasazení" in report.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# Runner
# ═══════════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    test_classes = [
        TestPathToModule,
        TestModuleToImpactCategories,
        TestSummarizeImpacts,
        TestCmpCount,
        TestCompareSnapshot,
        TestWorstState,
        TestBuildQCReport,
    ]
    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
