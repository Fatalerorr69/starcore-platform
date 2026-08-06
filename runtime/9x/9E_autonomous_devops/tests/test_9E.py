"""Tests for 9E Autonomous DevOps"""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "9E"


def test_pipeline_execution() -> None:
    from pipeline_orchestrator import Pipeline, PipelineStage, StageStatus

    calls: list[str] = []

    def build() -> dict:
        calls.append("build")
        return {"artifact": "app.tar.gz"}

    def deploy() -> dict:
        calls.append("deploy")
        return {"deployed": True}

    p = Pipeline(name="ci-cd")
    p.add_stage(PipelineStage("build", build))
    p.add_stage(PipelineStage("deploy", deploy, depends_on=["build"]))
    results = p.execute()
    assert results["build"] == StageStatus.SUCCESS
    assert results["deploy"] == StageStatus.SUCCESS
    assert calls == ["build", "deploy"]


def test_pipeline_skip_on_dependency_failure() -> None:
    from pipeline_orchestrator import Pipeline, PipelineStage, StageStatus

    def fail_stage() -> dict:
        raise RuntimeError("build failed")

    def deploy_stage() -> dict:
        return {}

    p = Pipeline(name="failing-ci")
    p.add_stage(PipelineStage("build", fail_stage, retry_limit=1))
    p.add_stage(PipelineStage("deploy", deploy_stage, depends_on=["build"]))
    results = p.execute()
    assert results["build"] == StageStatus.FAILED
    assert results["deploy"] == StageStatus.SKIPPED
