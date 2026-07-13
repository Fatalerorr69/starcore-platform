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


def test_get_run_returns_none_for_unknown_id():
    session = get_session()
    try:
        assert get_run(session, "does-not-exist") is None
    finally:
        session.close()
