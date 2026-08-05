#!/usr/bin/env python3
"""
Standalone tests for startup_protocol.py.

Spuštění: uv run python .starcore/scripts/tests/test_startup_protocol.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# ── Path setup ────────────────────────────────────────────────────────────────

_TESTS_DIR = Path(__file__).parent
_SCRIPTS_DIR = _TESTS_DIR.parent
sys.path.insert(0, str(_SCRIPTS_DIR))

from models import CheckState, SessionEntry  # noqa: E402
from startup_protocol import (  # noqa: E402
    GitInfo,
    RiskEntry,
    StartupState,
    _fmt_next_action,
    _fmt_session,
    collect_startup_state,
    format_startup_report,
    parse_decisions_content,
    parse_pending_work_content,
    parse_risks_content,
)

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_git(
    *,
    repo: str = "starcore-platform",
    remote: str = "github.com/Fatalerorr69/starcore-platform",
    branch: str = "main",
    head: str = "abc1234",
    head_msg: str = "feat: test commit",
    worktree_clean: bool = True,
    worktree_summary: str = "Cistý worktree",
) -> GitInfo:
    return GitInfo(
        repo=repo,
        remote=remote,
        branch=branch,
        head=head,
        head_msg=head_msg,
        worktree_clean=worktree_clean,
        worktree_summary=worktree_summary,
    )


def _make_session(
    *,
    session_id: str = "test-session-001",
    start_time: str = "2026-07-27T10:00:00Z",
    branch: str = "main",
    head: str = "abc1234",
    end_time: str | None = None,
    next_action: str = "",
    user_requests: list[str] | None = None,
) -> SessionEntry:
    return SessionEntry(
        session_id=session_id,
        start_time=start_time,
        branch=branch,
        head=head,
        end_time=end_time,
        next_action=next_action,
        user_requests=user_requests or [],
    )


def _make_state(
    *,
    git: GitInfo | None = None,
    last_session: SessionEntry | None = None,
    open_risks: list[RiskEntry] | None = None,
    p1_items: list[str] | None = None,
    recent_decisions: list[str] | None = None,
    sentinel_state: CheckState = CheckState.PASS,
    sentinel_detail: str = "7/7 dimenzí bez regrese",
    release_verdict: str = "RELEASE_READY",
    release_blockers: list[str] | None = None,
    quick: bool = False,
) -> StartupState:
    return StartupState(
        git=git or _make_git(),
        last_session=last_session,
        open_risks=open_risks or [],
        p1_items=p1_items or [],
        recent_decisions=recent_decisions or [],
        sentinel_state=sentinel_state,
        sentinel_detail=sentinel_detail,
        release_verdict=release_verdict,
        release_blockers=release_blockers or [],
        quick=quick,
    )


# ── Tests: GitInfo ────────────────────────────────────────────────────────────


class TestGitInfo(unittest.TestCase):
    def test_clean_worktree_fields(self):
        g = _make_git(worktree_clean=True, worktree_summary="Cistý worktree")
        self.assertTrue(g.worktree_clean)
        self.assertIn("worktree", g.worktree_summary.lower())

    def test_dirty_worktree_fields(self):
        g = _make_git(worktree_clean=False, worktree_summary="2 staged, 1 untracked")
        self.assertFalse(g.worktree_clean)
        self.assertIn("staged", g.worktree_summary)

    def test_repo_and_remote_fields(self):
        g = _make_git(repo="starcore-platform", remote="github.com/Fatalerorr69/starcore-platform")
        self.assertEqual(g.repo, "starcore-platform")
        self.assertIn("github.com", g.remote)

    def test_head_and_message(self):
        g = _make_git(head="abc1234", head_msg="feat: add feature")
        self.assertEqual(g.head, "abc1234")
        self.assertEqual(g.head_msg, "feat: add feature")


# ── Tests: RiskEntry ─────────────────────────────────────────────────────────


class TestRiskEntry(unittest.TestCase):
    def test_fields(self):
        r = RiskEntry(id="R-001", title="SHA pinning", severity="HIGH", status="OPEN")
        self.assertEqual(r.id, "R-001")
        self.assertEqual(r.severity, "HIGH")
        self.assertEqual(r.status, "OPEN")

    def test_multiple_risks(self):
        risks = [
            RiskEntry("R-001", "title A", "HIGH", "OPEN"),
            RiskEntry("R-007", "title B", "MEDIUM", "OPEN"),
        ]
        self.assertEqual(len(risks), 2)
        self.assertEqual(risks[0].severity, "HIGH")


# ── Tests: parse_risks_content ────────────────────────────────────────────────


SAMPLE_RISKS_MD = (
    "# Risk Register\n\n"
    "## CRITICAL / HIGH\n\n"
    "### R-001 -- GitHub Actions SHA pinning\n"
    "- **Stav:** OPEN\n"
    "- **Zavaznost:** HIGH\n\n"
    "### R-002 -- Closed risk\n"
    "- **Stav:** CLOSED\n"
    "- **Zavaznost:** HIGH\n\n"
    "## MEDIUM\n\n"
    "### R-007 -- Inactive workflow\n"
    "- **Stav:** OPEN / ACCEPTED pending operator decision\n"
    "- **Zavaznost:** MEDIUM\n"
)

# Version with proper Czech diacritics for field matching
SAMPLE_RISKS_CZECH = (
    "# Risk Register\n\n"
    "### R-001 -- GitHub Actions SHA pinning\n"
    "- **Stav:** OPEN\n"
    "- **Závažnost:** HIGH\n\n"
    "### R-002 -- Closed risk\n"
    "- **Stav:** CLOSED\n"
    "- **Závažnost:** HIGH\n\n"
    "### R-007 -- Inactive workflow\n"
    "- **Stav:** OPEN / ACCEPTED\n"
    "- **Závažnost:** MEDIUM\n"
)


class TestParseRisksContent(unittest.TestCase):
    def test_parses_open_risks(self):
        risks = parse_risks_content(SAMPLE_RISKS_CZECH)
        ids = [r.id for r in risks]
        self.assertIn("R-001", ids)
        self.assertIn("R-007", ids)

    def test_excludes_closed_risks(self):
        risks = parse_risks_content(SAMPLE_RISKS_CZECH)
        ids = [r.id for r in risks]
        self.assertNotIn("R-002", ids)

    def test_sorted_by_severity_descending(self):
        risks = parse_risks_content(SAMPLE_RISKS_CZECH)
        self.assertGreater(len(risks), 0)
        # First entry should have highest severity
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        vals = [severity_order.get(r.severity, 0) for r in risks]
        self.assertEqual(vals, sorted(vals, reverse=True))

    def test_empty_content_returns_empty(self):
        risks = parse_risks_content("")
        self.assertEqual(risks, [])

    def test_no_open_risks_returns_empty(self):
        content = "### R-001 -- Something\n- **Stav:** CLOSED\n- **Závažnost:** HIGH\n"
        risks = parse_risks_content(content)
        self.assertEqual(risks, [])

    def test_risk_id_captured(self):
        risks = parse_risks_content(SAMPLE_RISKS_CZECH)
        r001 = next((r for r in risks if r.id == "R-001"), None)
        self.assertIsNotNone(r001)

    def test_risk_title_captured(self):
        risks = parse_risks_content(SAMPLE_RISKS_CZECH)
        r001 = next((r for r in risks if r.id == "R-001"), None)
        self.assertIsNotNone(r001)
        self.assertIn("GitHub", r001.title)  # type: ignore[union-attr]

    def test_open_slash_accepted_counts_as_open(self):
        risks = parse_risks_content(SAMPLE_RISKS_CZECH)
        r007 = next((r for r in risks if r.id == "R-007"), None)
        self.assertIsNotNone(r007)
        self.assertEqual(r007.status, "OPEN")  # type: ignore[union-attr]


# ── Tests: parse_pending_work_content ────────────────────────────────────────


SAMPLE_PENDING_MD = (
    "# Pending Work\n\n"
    "## P1 -- Vyresit brzy\n\n"
    "### R-001: GitHub Actions SHA pinning\n"
    "- Popis: fix\n\n"
    "### R-012: assert guards\n"
    "- Popis: quick win\n\n"
    "## P2 -- Deferrable\n\n"
    "### R-007: Inactive workflow\n"
)


class TestParsePendingWorkContent(unittest.TestCase):
    def test_extracts_p1_items(self):
        items = parse_pending_work_content(SAMPLE_PENDING_MD)
        self.assertEqual(len(items), 2)
        self.assertIn("R-001: GitHub Actions SHA pinning", items)

    def test_excludes_p2_items(self):
        items = parse_pending_work_content(SAMPLE_PENDING_MD)
        self.assertNotIn("R-007: Inactive workflow", items)

    def test_empty_content(self):
        items = parse_pending_work_content("")
        self.assertEqual(items, [])

    def test_no_p1_section(self):
        content = "## P2 -- Deferrable\n### Something\n"
        items = parse_pending_work_content(content)
        self.assertEqual(items, [])

    def test_both_p1_items_found(self):
        items = parse_pending_work_content(SAMPLE_PENDING_MD)
        self.assertIn("R-012: assert guards", items)


# ── Tests: parse_decisions_content ───────────────────────────────────────────


SAMPLE_DECISIONS_MD = (
    "# Working Decisions\n\n"
    "## D-001 -- Use asyncio.create_task\n"
    "Detail here.\n\n"
    "## D-002 -- Real async timing\n"
    "Detail here.\n\n"
    "## D-003 -- .starcore/ versioned in repo\n"
    "Detail here.\n"
)


class TestParseDecisionsContent(unittest.TestCase):
    def test_returns_most_recent_first(self):
        decisions = parse_decisions_content(SAMPLE_DECISIONS_MD)
        self.assertTrue(decisions[0].startswith("D-003"))

    def test_respects_limit(self):
        decisions = parse_decisions_content(SAMPLE_DECISIONS_MD, limit=2)
        self.assertEqual(len(decisions), 2)

    def test_empty_content(self):
        decisions = parse_decisions_content("")
        self.assertEqual(decisions, [])

    def test_single_decision(self):
        content = "## D-001 -- Single decision\nDetail.\n"
        decisions = parse_decisions_content(content)
        self.assertEqual(len(decisions), 1)
        self.assertIn("D-001", decisions[0])

    def test_default_limit_is_3(self):
        decisions = parse_decisions_content(SAMPLE_DECISIONS_MD)
        self.assertLessEqual(len(decisions), 3)


# ── Tests: _fmt_session ───────────────────────────────────────────────────────


class TestFmtSession(unittest.TestCase):
    def test_none_returns_no_previous(self):
        result = _fmt_session(None)
        self.assertIn("Žádná", result)

    def test_active_session(self):
        s = _make_session(session_id="sess-001", start_time="2026-07-27T10:00:00Z")
        result = _fmt_session(s)
        self.assertIn("sess-001", result)
        self.assertIn("aktivní", result)
        self.assertIn("2026-07-27", result)

    def test_ended_session(self):
        s = _make_session(end_time="2026-07-27T12:00:00Z")
        result = _fmt_session(s)
        self.assertIn("ukončena", result)

    def test_includes_request_count(self):
        s = _make_session(user_requests=["req1", "req2", "req3"])
        result = _fmt_session(s)
        self.assertIn("3 požadavků", result)

    def test_zero_requests(self):
        s = _make_session(user_requests=[])
        result = _fmt_session(s)
        self.assertIn("0 požadavků", result)


# ── Tests: _fmt_next_action ───────────────────────────────────────────────────


class TestFmtNextAction(unittest.TestCase):
    def test_uses_session_next_action_first(self):
        s = _make_session(next_action="Opravit R-001 SHA pinning")
        state = _make_state(last_session=s)
        result = _fmt_next_action(state)
        self.assertEqual(result, "Opravit R-001 SHA pinning")

    def test_falls_back_to_p1_item_when_no_session(self):
        state = _make_state(last_session=None, p1_items=["R-001: SHA pinning"])
        result = _fmt_next_action(state)
        self.assertEqual(result, "R-001: SHA pinning")

    def test_falls_back_to_p1_when_session_has_no_next_action(self):
        s = _make_session(next_action="")
        state = _make_state(last_session=s, p1_items=["R-001: SHA pinning"])
        result = _fmt_next_action(state)
        self.assertEqual(result, "R-001: SHA pinning")

    def test_falls_back_to_sentinel_fix_on_fail(self):
        state = _make_state(
            last_session=None,
            p1_items=[],
            sentinel_state=CheckState.FAIL,
        )
        result = _fmt_next_action(state)
        self.assertIn("regrese", result.lower())

    def test_falls_back_to_audit_when_all_empty(self):
        state = _make_state(last_session=None, p1_items=[], sentinel_state=CheckState.PASS)
        result = _fmt_next_action(state)
        self.assertIn("qc_engine", result)


# ── Tests: format_startup_report ──────────────────────────────────────────────


class TestFormatStartupReport(unittest.TestCase):
    def setUp(self):
        self.state = _make_state(
            git=_make_git(repo="starcore-platform", branch="main", head="abc1234"),
            last_session=_make_session(),
            open_risks=[RiskEntry("R-001", "SHA pinning", "HIGH", "OPEN")],
            p1_items=["R-001: SHA pinning"],
            recent_decisions=["D-003 -- .starcore/ versioned"],
            sentinel_state=CheckState.PASS,
            sentinel_detail="7/7 dimenzí bez regrese",
            release_verdict="RELEASE_READY_WITH_WARNINGS",
        )

    def test_contains_header(self):
        report = format_startup_report(self.state)
        self.assertIn("STARCORE SESSION STATUS", report)

    def test_contains_repo_name(self):
        report = format_startup_report(self.state)
        self.assertIn("starcore-platform", report)

    def test_contains_branch(self):
        report = format_startup_report(self.state)
        self.assertIn("main", report)

    def test_contains_head(self):
        report = format_startup_report(self.state)
        self.assertIn("abc1234", report)

    def test_contains_risk(self):
        report = format_startup_report(self.state)
        self.assertIn("R-001", report)

    def test_contains_verdict(self):
        report = format_startup_report(self.state)
        self.assertIn("PŘIPRAVEN", report)

    def test_contains_volby_menu(self):
        report = format_startup_report(self.state)
        self.assertIn("VOLBY:", report)
        self.assertIn("[1]", report)
        self.assertIn("[6]", report)

    def test_sentinel_pass_shown(self):
        report = format_startup_report(self.state)
        self.assertIn("PASS", report)

    def test_dirty_worktree_warning(self):
        state = _make_state(git=_make_git(worktree_clean=False, worktree_summary="2 staged"))
        report = format_startup_report(state)
        self.assertIn("uncommitted", report)

    def test_no_risks_message(self):
        state = _make_state(open_risks=[])
        report = format_startup_report(state)
        self.assertIn("rizika", report)

    def test_sentinel_fail_shown(self):
        state = _make_state(
            sentinel_state=CheckState.FAIL,
            sentinel_detail="REGRESE: test_count",
        )
        report = format_startup_report(state)
        self.assertIn("FAIL", report)

    def test_quick_mode_shown(self):
        state = _make_state(
            quick=True,
            sentinel_state=CheckState.UNKNOWN,
            sentinel_detail="Preskoceno (--quick)",
        )
        report = format_startup_report(state)
        self.assertIn("Preskoceno", report)

    def test_separator_present(self):
        report = format_startup_report(self.state)
        self.assertIn("═", report)


# ── Tests: StartupState.to_dict ───────────────────────────────────────────────


class TestStartupStateToDict(unittest.TestCase):
    def test_serializes_correctly(self):
        state = _make_state(
            open_risks=[RiskEntry("R-001", "SHA", "HIGH", "OPEN")],
            p1_items=["item1"],
        )
        d = state.to_dict()
        self.assertIn("git", d)
        self.assertIn("open_risks", d)
        self.assertEqual(len(d["open_risks"]), 1)
        self.assertEqual(d["open_risks"][0]["id"], "R-001")
        self.assertIn("sentinel_state", d)
        self.assertEqual(d["p1_items"], ["item1"])

    def test_no_last_session(self):
        state = _make_state(last_session=None)
        d = state.to_dict()
        self.assertIsNone(d["last_session"])

    def test_with_last_session(self):
        state = _make_state(last_session=_make_session(session_id="s-001"))
        d = state.to_dict()
        self.assertIsNotNone(d["last_session"])
        self.assertEqual(d["last_session"]["session_id"], "s-001")

    def test_quick_flag_serialized(self):
        state = _make_state(quick=True)
        d = state.to_dict()
        self.assertTrue(d["quick"])


# ── Tests: collect_startup_state (mocked) ────────────────────────────────────


class TestCollectStartupState(unittest.TestCase):
    def _defaults(self):
        return (
            _make_git(),
            _make_session(),
            [RiskEntry("R-001", "SHA", "HIGH", "OPEN")],
            ["R-001: SHA pinning"],
            ["D-003 -- starcore versioned"],
        )

    @patch("startup_protocol.step_git_info")
    @patch("startup_protocol.step_load_last_session")
    @patch("startup_protocol.step_load_risks")
    @patch("startup_protocol.step_load_pending_work")
    @patch("startup_protocol.step_load_decisions")
    @patch("startup_protocol.step_verify_sentinel")
    @patch("startup_protocol.step_verify_github")
    def test_collect_calls_all_steps(
        self, m_github, m_sentinel, m_decisions, m_pending, m_risks, m_session, m_git
    ):
        git, session, risks, p1, decisions = self._defaults()
        m_git.return_value = git
        m_session.return_value = session
        m_risks.return_value = risks
        m_pending.return_value = p1
        m_decisions.return_value = decisions
        m_sentinel.return_value = (CheckState.PASS, "7/7 ok")
        m_github.return_value = ("RELEASE_READY_WITH_WARNINGS", ["R-001"])

        state = collect_startup_state(quick=False)

        m_git.assert_called_once()
        m_session.assert_called_once()
        m_risks.assert_called_once()
        m_pending.assert_called_once()
        m_decisions.assert_called_once()
        m_sentinel.assert_called_once()
        m_github.assert_called_once()
        self.assertIsInstance(state, StartupState)

    @patch("startup_protocol.step_git_info")
    @patch("startup_protocol.step_load_last_session")
    @patch("startup_protocol.step_load_risks")
    @patch("startup_protocol.step_load_pending_work")
    @patch("startup_protocol.step_load_decisions")
    @patch("startup_protocol.step_verify_sentinel")
    @patch("startup_protocol.step_verify_github")
    def test_quick_mode_skips_verification(
        self, m_github, m_sentinel, m_decisions, m_pending, m_risks, m_session, m_git
    ):
        git, session, risks, p1, decisions = self._defaults()
        m_git.return_value = git
        m_session.return_value = session
        m_risks.return_value = risks
        m_pending.return_value = p1
        m_decisions.return_value = decisions

        state = collect_startup_state(quick=True)

        m_sentinel.assert_not_called()
        m_github.assert_not_called()
        self.assertTrue(state.quick)
        self.assertEqual(state.sentinel_state, CheckState.UNKNOWN)

    @patch("startup_protocol.step_git_info")
    @patch("startup_protocol.step_load_last_session")
    @patch("startup_protocol.step_load_risks")
    @patch("startup_protocol.step_load_pending_work")
    @patch("startup_protocol.step_load_decisions")
    @patch("startup_protocol.step_verify_sentinel")
    @patch("startup_protocol.step_verify_github")
    def test_state_fields_populated(
        self, m_github, m_sentinel, m_decisions, m_pending, m_risks, m_session, m_git
    ):
        git, session, risks, p1, decisions = self._defaults()
        m_git.return_value = git
        m_session.return_value = session
        m_risks.return_value = risks
        m_pending.return_value = p1
        m_decisions.return_value = decisions
        m_sentinel.return_value = (CheckState.PASS, "7/7 ok")
        m_github.return_value = ("RELEASE_READY", [])

        state = collect_startup_state(quick=False)

        self.assertEqual(state.git.repo, "starcore-platform")
        self.assertEqual(state.open_risks[0].id, "R-001")
        self.assertEqual(state.p1_items[0], "R-001: SHA pinning")
        self.assertEqual(state.sentinel_state, CheckState.PASS)
        self.assertEqual(state.release_verdict, "RELEASE_READY")


# ── Runner ────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestGitInfo,
        TestRiskEntry,
        TestParseRisksContent,
        TestParsePendingWorkContent,
        TestParseDecisionsContent,
        TestFmtSession,
        TestFmtNextAction,
        TestFormatStartupReport,
        TestStartupStateToDict,
        TestCollectStartupState,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
