"""
Persistence Models
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _new_id() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(UTC)


class BlueprintRunRecord(Base):
    __tablename__ = "blueprint_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_new_id)
    blueprint_name: Mapped[str] = mapped_column(String)
    version: Mapped[str] = mapped_column(String)
    parallel: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    tasks: Mapped[list[TaskRunRecord]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class TaskRunRecord(Base):
    __tablename__ = "task_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_new_id)
    run_id: Mapped[str] = mapped_column(ForeignKey("blueprint_runs.id"))
    task_id: Mapped[str] = mapped_column(String)
    provider: Mapped[str] = mapped_column(String)
    resource: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    result: Mapped[dict] = mapped_column(JSON, default=dict)

    run: Mapped[BlueprintRunRecord] = relationship(back_populates="tasks")
