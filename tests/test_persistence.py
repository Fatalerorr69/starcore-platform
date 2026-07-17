"""
Persistence Tests
"""

from __future__ import annotations

from core.database import get_session
from core.repository import get_run, list_runs, save_run
from orchestrator.task import Task, TaskStatus


def _sample_tasks() -> list[Task]:
    task = Task(id="t1", provider="fake", action="create", resource="thing")
    task.status = TaskStatus.SUCCESS
    task.result = {"vmid": 105}
    return [task]


def test_save_and_get_run_roundtrip():
    session = get_session()
    try:
        record = save_run(session, "demo", "1.0", False, _sample_tasks())
        assert record.id

        fetched = get_run(session, record.id)
        assert fetched is not None
        assert fetched.blueprint_name == "demo"
        assert len(fetched.tasks) == 1
        assert fetched.tasks[0].result == {"vmid": 105}
    finally:
        session.close()


def test_list_runs_includes_saved_run():
    session = get_session()
    try:
        save_run(session, "demo-list", "1.0", True, _sample_tasks())
        runs = list_runs(session)
        assert any(r.blueprint_name == "demo-list" for r in runs)
    finally:
        session.close()


def test_list_runs_pagination_limits_and_offsets_newest_first():
    """TD-20 regression test: list_runs() supports limit/offset while
    preserving newest-first ordering; calling it with no arguments keeps
    the original unbounded behavior (used by the CLI).
    """
    session = get_session()
    try:
        for i in range(5):
            save_run(session, f"bp-{i}", "1.0", False, _sample_tasks())

        newest_two = list_runs(session, limit=2)
        assert [r.blueprint_name for r in newest_two] == ["bp-4", "bp-3"]

        next_two = list_runs(session, limit=2, offset=2)
        assert [r.blueprint_name for r in next_two] == ["bp-2", "bp-1"]

        everything = list_runs(session)
        assert len(everything) == 5
    finally:
        session.close()


def test_get_run_returns_none_for_unknown_id():
    session = get_session()
    try:
        assert get_run(session, "does-not-exist") is None
    finally:
        session.close()
