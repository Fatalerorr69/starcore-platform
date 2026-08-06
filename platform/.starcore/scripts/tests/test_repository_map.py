#!/usr/bin/env python3
"""
Standalone tests for repository_map.py.

Spuštění: uv run python .starcore/scripts/tests/test_repository_map.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# ── Path setup ────────────────────────────────────────────────────────────────

_TESTS_DIR = Path(__file__).parent
_SCRIPTS_DIR = _TESTS_DIR.parent
sys.path.insert(0, str(_SCRIPTS_DIR))

from repository_map import (  # noqa: E402
    Classification,
    RepositoryEntry,
    classify,
    compute_diff,
    git_activity,
    load_state,
    scan,
)

_REQUIRED_ENTRY_FIELDS = {
    "path",
    "classification",
    "reason",
    "detected_files",
    "git_activity",
    "confidence",
    "notes",
}


def _make_fake_repo(root: Path) -> None:
    """Build a minimal git repository with a platform/, a known-legacy dir,
    and an unmapped directory, and commit it."""
    (root / "platform" / "packages").mkdir(parents=True)
    (root / "platform" / "packages" / "x.py").write_text("x = 1\n")
    (root / "runtime").mkdir()
    (root / "runtime" / "state.json").write_text("{}\n")
    (root / "mystery_new_dir").mkdir()
    (root / "mystery_new_dir" / "readme.txt").write_text("hello\n")

    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.local"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "initial fake repo"],
        cwd=root,
        check=True,
    )


class RepoMapTestCase(unittest.TestCase):
    """Base class providing a fresh fake git repo per test.

    The state file lives in a separate temporary directory, entirely
    outside repo_root — mirroring real usage, where
    platform/.starcore/state/repository_map.json sits *inside* the
    already-classified platform/ subtree rather than as a sibling
    top-level directory of the scanned root. Placing it inside
    repo_root here would make scan()'s own output directory appear as
    a new top-level entry on a subsequent scan — a fixture artifact,
    not something that can happen in the real repository layout.
    """

    def setUp(self) -> None:
        self._repo_tmpdir = tempfile.TemporaryDirectory()
        self._state_tmpdir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self._repo_tmpdir.name)
        _make_fake_repo(self.repo_root)
        self.state_path = Path(self._state_tmpdir.name) / "repository_map.json"

    def tearDown(self) -> None:
        self._repo_tmpdir.cleanup()
        self._state_tmpdir.cleanup()


class TestClassify(unittest.TestCase):
    """Pure classification logic — no filesystem or git involved."""

    def test_platform_is_production(self):
        classification, _reason, confidence = classify("platform")
        self.assertEqual(classification, Classification.PRODUCTION)
        self.assertEqual(confidence, "HIGH")

    def test_known_legacy_dir_is_legacy(self):
        classification, _reason, confidence = classify("runtime")
        self.assertEqual(classification, Classification.LEGACY)
        self.assertEqual(confidence, "HIGH")

    def test_unmapped_dir_is_unknown_not_legacy(self):
        classification, _reason, _confidence = classify("mystery_new_dir")
        self.assertEqual(classification, Classification.UNKNOWN)
        self.assertNotEqual(classification, Classification.LEGACY)

    def test_all_legacy_allowlist_members_classify_legacy(self):
        # Spot-check a representative sample rather than the whole set.
        for name in ("autonomous", "distributed", "ai_core", "sdk", "core"):
            classification, _reason, _confidence = classify(name)
            self.assertEqual(classification, Classification.LEGACY, name)


class TestScan(RepoMapTestCase):
    def test_scan_classifies_fake_repo_correctly(self):
        snapshot = scan(repo_root=self.repo_root, state_path=self.state_path, write=True)
        by_path = {e["path"]: e for e in snapshot["entries"]}

        self.assertEqual(by_path["platform/"]["classification"], "PRODUCTION")
        self.assertEqual(by_path["runtime/"]["classification"], "LEGACY")
        self.assertEqual(by_path["mystery_new_dir/"]["classification"], "UNKNOWN")

    def test_scan_writes_only_state_file(self):
        before = {
            p.relative_to(self.repo_root)
            for p in self.repo_root.rglob("*")
            if ".git" not in p.parts
        }
        self.assertFalse(self.state_path.exists())

        scan(repo_root=self.repo_root, state_path=self.state_path, write=True)

        after = {
            p.relative_to(self.repo_root)
            for p in self.repo_root.rglob("*")
            if ".git" not in p.parts
        }
        # Nothing changes inside the scanned repository tree itself...
        self.assertEqual(after, before)
        # ...the only write lands exactly at the given state_path.
        self.assertTrue(self.state_path.exists())
        self.assertTrue(self.state_path.is_file())

    def test_scan_write_false_does_not_create_state_file(self):
        scan(repo_root=self.repo_root, state_path=self.state_path, write=False)
        self.assertFalse(self.state_path.exists())

    def test_scan_never_deletes_or_moves(self):
        with (
            patch("os.remove") as mock_remove,
            patch("os.unlink") as mock_unlink,
            patch("shutil.rmtree") as mock_rmtree,
            patch("shutil.move") as mock_move,
            patch.object(Path, "unlink", autospec=True) as mock_path_unlink,
        ):
            scan(repo_root=self.repo_root, state_path=self.state_path, write=True)

        mock_remove.assert_not_called()
        mock_unlink.assert_not_called()
        mock_rmtree.assert_not_called()
        mock_move.assert_not_called()
        mock_path_unlink.assert_not_called()

    def test_json_schema_has_required_fields(self):
        snapshot = scan(repo_root=self.repo_root, state_path=self.state_path, write=True)

        self.assertIn("schema_version", snapshot)
        self.assertIn("generated_at", snapshot)
        self.assertIn("repo_root_commit", snapshot)
        self.assertIn("entries", snapshot)
        self.assertTrue(snapshot["entries"])

        for entry in snapshot["entries"]:
            self.assertEqual(set(entry.keys()), _REQUIRED_ENTRY_FIELDS)

        # Written file must be valid, parseable JSON matching the in-memory snapshot.
        with open(self.state_path) as f:
            on_disk = json.load(f)
        self.assertEqual(on_disk, snapshot)

    def test_repository_entry_round_trip(self):
        entry = RepositoryEntry(
            path="runtime/",
            classification=Classification.LEGACY,
            reason="test",
            detected_files=["runtime/a.json"],
            git_activity={"commit_count": 1, "last_commit": None},
            confidence="HIGH",
            notes="",
        )
        restored = RepositoryEntry.from_dict(entry.to_dict())
        self.assertEqual(entry, restored)


class TestGitActivity(RepoMapTestCase):
    def test_git_activity_counts_commits_read_only(self):
        activity = git_activity(self.repo_root, "runtime")
        self.assertGreaterEqual(activity["commit_count"], 1)
        self.assertIsNotNone(activity["last_commit"])

    def test_git_activity_never_mutates(self):
        with (
            patch("shutil.rmtree") as mock_rmtree,
            patch("shutil.move") as mock_move,
        ):
            git_activity(self.repo_root, "platform")
        mock_rmtree.assert_not_called()
        mock_move.assert_not_called()


class TestDiff(RepoMapTestCase):
    def test_diff_detects_new_directory(self):
        old = scan(repo_root=self.repo_root, state_path=self.state_path, write=True)
        (self.repo_root / "brand_new_dir").mkdir()
        new = scan(repo_root=self.repo_root, state_path=self.state_path, write=False)

        result = compute_diff(old, new)
        self.assertIn("brand_new_dir/", result["added"])
        self.assertEqual(result["removed"], [])

    def test_diff_detects_removed_directory(self):
        old = scan(repo_root=self.repo_root, state_path=self.state_path, write=True)
        shutil.rmtree(self.repo_root / "mystery_new_dir")
        new = scan(repo_root=self.repo_root, state_path=self.state_path, write=False)

        result = compute_diff(old, new)
        self.assertIn("mystery_new_dir/", result["removed"])
        self.assertEqual(result["added"], [])

    def test_diff_detects_classification_change(self):
        old = scan(repo_root=self.repo_root, state_path=self.state_path, write=True)
        # Simulate a prior snapshot that had classified runtime/ differently
        # (e.g. before ADR-020 existed) — mutate the loaded dict, not the
        # classify() logic itself.
        mutated_old = json.loads(json.dumps(old))
        for entry in mutated_old["entries"]:
            if entry["path"] == "runtime/":
                entry["classification"] = "UNKNOWN"

        new = scan(repo_root=self.repo_root, state_path=self.state_path, write=False)
        result = compute_diff(mutated_old, new)

        self.assertIn("runtime/", result["changed"])

    def test_diff_no_previous_state_returns_none_old(self):
        self.assertIsNone(load_state(self.state_path))
        new = scan(repo_root=self.repo_root, state_path=self.state_path, write=False)
        result = compute_diff(None, new)
        # Every current entry looks "added" relative to no prior state.
        self.assertEqual(set(result["added"]), set(result["new_entries"].keys()))

    def test_diff_has_unknown_true_triggers_exit_1_condition(self):
        new = scan(repo_root=self.repo_root, state_path=self.state_path, write=False)
        result = compute_diff(None, new)
        # mystery_new_dir/ is UNKNOWN by construction of the fake repo.
        self.assertTrue(result["has_unknown"])

    def test_diff_no_unknown_does_not_trigger(self):
        # Remove the one UNKNOWN-producing directory and re-scan.
        shutil.rmtree(self.repo_root / "mystery_new_dir")
        new = scan(repo_root=self.repo_root, state_path=self.state_path, write=False)
        result = compute_diff(None, new)
        self.assertFalse(result["has_unknown"])

    def test_diff_never_writes_state_file(self):
        scan(repo_root=self.repo_root, state_path=self.state_path, write=True)
        mtime_before = self.state_path.stat().st_mtime
        new = scan(repo_root=self.repo_root, state_path=self.state_path, write=False)
        compute_diff(load_state(self.state_path), new)
        mtime_after = self.state_path.stat().st_mtime
        self.assertEqual(mtime_before, mtime_after)


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestClassify,
        TestScan,
        TestGitActivity,
        TestDiff,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
