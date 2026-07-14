"""
CLI Tests
"""

from pathlib import Path

from typer.testing import CliRunner

from apps.cli.main import app

runner = CliRunner()
EXAMPLE_PATH = str(
    Path(__file__).parent.parent / "packages" / "blueprints" / "examples" / "basic.yaml"
)


def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "STARCORE Platform" in result.stdout


def test_health_command():
    result = runner.invoke(app, ["health"])
    assert result.exit_code == 0
    assert "System OK" in result.stdout


def test_blueprint_plan_command():
    result = runner.invoke(app, ["blueprint", "plan", EXAMPLE_PATH])
    assert result.exit_code == 0
    assert "web-vm" in result.stdout
    assert "postgres" in result.stdout


def test_blueprint_run_command_reports_failures():
    result = runner.invoke(app, ["blueprint", "run", EXAMPLE_PATH])
    assert result.exit_code == 1
    assert "failed" in result.stdout.lower()


def test_blueprint_run_parallel_flag_reports_failures():
    result = runner.invoke(app, ["blueprint", "run", EXAMPLE_PATH, "--parallel"])
    assert result.exit_code == 1
    assert "failed" in result.stdout.lower()


def test_blueprint_run_persists_and_appears_in_runs_list():
    runner.invoke(app, ["blueprint", "run", EXAMPLE_PATH])
    result = runner.invoke(app, ["runs", "list"])
    assert result.exit_code == 0
    assert "demo" in result.stdout


def test_runs_show_displays_persisted_run():
    from core.database import get_session
    from core.repository import list_runs

    runner.invoke(app, ["blueprint", "run", EXAMPLE_PATH])

    session = get_session()
    try:
        records = list_runs(session)
    finally:
        session.close()

    assert records
    run_id = records[0].id

    result = runner.invoke(app, ["runs", "show", run_id])
    assert result.exit_code == 0
    assert "demo" in result.stdout


def test_runs_show_unknown_id_returns_error():
    result = runner.invoke(app, ["runs", "show", "does-not-exist"])
    assert result.exit_code == 1


def test_plugins_command_lists_example_plugin():
    result = runner.invoke(app, ["plugins"])
    assert result.exit_code == 0
    assert "example_provider" in result.stdout


def test_diagnose_command_runs_and_prints_report():
    result = runner.invoke(app, ["diagnose"])
    assert result.exit_code in (0, 1)
    assert "overall status" in result.stdout.lower()
