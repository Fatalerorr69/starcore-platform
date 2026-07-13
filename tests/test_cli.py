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
