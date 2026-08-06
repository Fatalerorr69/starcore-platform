"""9E — Autonomous DevOps: Pipeline Orchestrator"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable
import uuid


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PipelineStage:
    name: str
    runner: Callable[[], dict[str, Any]]
    depends_on: list[str] = field(default_factory=list)
    retry_limit: int = 3
    status: StageStatus = StageStatus.PENDING
    output: dict[str, Any] = field(default_factory=dict)


@dataclass
class Pipeline:
    pipeline_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    stages: list[PipelineStage] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_stage(self, stage: PipelineStage) -> None:
        self.stages.append(stage)

    def execute(self) -> dict[str, StageStatus]:
        completed: set[str] = set()
        results: dict[str, StageStatus] = {}

        for stage in self.stages:
            if not all(dep in completed for dep in stage.depends_on):
                stage.status = StageStatus.SKIPPED
                results[stage.name] = stage.status
                continue

            for attempt in range(stage.retry_limit):
                try:
                    stage.status = StageStatus.RUNNING
                    stage.output = stage.runner()
                    stage.status = StageStatus.SUCCESS
                    completed.add(stage.name)
                    break
                except Exception:
                    if attempt == stage.retry_limit - 1:
                        stage.status = StageStatus.FAILED
            results[stage.name] = stage.status

        return results
