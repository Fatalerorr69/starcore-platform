"""
Task Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(slots=True)
class Task:
    id: str
    provider: str
    action: str
    resource: str

    payload: dict[str, Any] = field(default_factory=dict)

    depends_on: list[str] = field(default_factory=list)

    status: TaskStatus = TaskStatus.PENDING
