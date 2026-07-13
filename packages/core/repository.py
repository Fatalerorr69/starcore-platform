"""
Run History Repository
"""

from __future__ import annotations

from orchestrator.task import Task
from sqlalchemy.orm import Session

from .models_db import BlueprintRunRecord, TaskRunRecord


def save_run(
    session: Session,
    blueprint_name: str,
    version: str,
    parallel: bool,
    tasks: list[Task],
) -> BlueprintRunRecord:
    run = BlueprintRunRecord(blueprint_name=blueprint_name, version=version, parallel=parallel)
    for task in tasks:
        run.tasks.append(
            TaskRunRecord(
                task_id=task.id,
                provider=task.provider,
                resource=task.resource,
                status=task.status.value,
                result=task.result,
            )
        )
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def list_runs(session: Session) -> list[BlueprintRunRecord]:
    return session.query(BlueprintRunRecord).order_by(BlueprintRunRecord.created_at.desc()).all()


def get_run(session: Session, run_id: str) -> BlueprintRunRecord | None:
    return session.get(BlueprintRunRecord, run_id)
