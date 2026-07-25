"""
CLI Tests
"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

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


def test_ai_generate_command_fails_gracefully_without_api_key():
    result = runner.invoke(app, ["ai", "generate", "a simple web app"])
    assert result.exit_code == 1
    assert "anthropic" in result.stdout.lower() or "not configured" in result.stdout.lower()


def test_proxmox_discover_command_reports_connection_failure_without_credentials():
    result = runner.invoke(app, ["proxmox", "discover"])
    assert result.exit_code == 1
    assert "could not connect" in result.stdout.lower()


def test_resource_action_command_reports_skipped_for_unknown_provider():
    result = runner.invoke(app, ["resource", "action", "ghost", "stop", "thing"])
    assert result.exit_code == 0
    assert "skipped" in result.stdout.lower()


def test_snapshot_create_reports_failure_without_proxmox_connection():
    result = runner.invoke(app, ["snapshot", "create", "fatalab", "105", "before-test"])
    assert result.exit_code == 1


def test_snapshot_list_reports_failure_without_proxmox_connection():
    result = runner.invoke(app, ["snapshot", "list", "fatalab", "105"])
    assert result.exit_code == 1


def test_snapshot_delete_prompts_for_confirmation():
    result = runner.invoke(app, ["snapshot", "delete", "fatalab", "105", "old-snap"], input="n\n")
    assert result.exit_code == 0
    assert "delete" in result.stdout.lower()


def test_snapshot_delete_skips_confirmation_with_yes_flag():
    result = runner.invoke(app, ["snapshot", "delete", "fatalab", "105", "old-snap", "--yes"])
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_task(status_val: str, result_dict: dict | None = None) -> MagicMock:
    task = MagicMock()
    task.status.value = status_val
    task.result = result_dict or {}
    return task


_VALID_BLUEPRINT_YAML = """\
name: gen-test
version: "1.0"
resources:
  - name: web
    provider: docker
    kind: container
"""


# ---------------------------------------------------------------------------
# plugins: no-plugins path (lines 211-212)
# ---------------------------------------------------------------------------


def test_plugins_list_no_plugins_found():
    with patch("core.plugin_manager.plugin_manager") as mock_pm:
        mock_pm.discover.return_value = []
        result = runner.invoke(app, ["plugins"])
    assert result.exit_code == 0
    assert "No plugins found" in result.stdout


# ---------------------------------------------------------------------------
# diagnose: proxmox nodes/storage/orphaned + docker containers (lines 252-295)
# ---------------------------------------------------------------------------


def test_diagnose_renders_proxmox_and_docker_sections():
    report = {
        "overall_status": "ok",
        "runtime_environment": "local",
        "environment_details": {
            "os_platform": {"system": "Linux", "release": "6.1", "is_wsl": False},
            "cloud_provider": None,
        },
        "checks": [{"name": "db", "status": "ok", "detail": "alive"}],
        "proxmox": {
            "nodes": [
                {
                    "node": "pve",
                    "cpu_percent": 10,
                    "memory_used_gb": 4,
                    "memory_total_gb": 16,
                    "disk_used_gb": 20,
                    "disk_total_gb": 100,
                }
            ],
            "storage": [
                {
                    "node": "pve",
                    "storage": "local",
                    "type": "dir",
                    "used_gb": 5,
                    "total_gb": 50,
                }
            ],
            "orphaned_resources": [{"kind": "vm", "vmid": 999, "name": "old-vm", "node": "pve"}],
        },
        "docker": {"containers": {"running": 3}},
    }
    with patch("apps.cli.main.run_diagnostics", new=AsyncMock(return_value=report)):
        result = runner.invoke(app, ["diagnose"])
    assert result.exit_code == 0
    assert "pve" in result.stdout
    assert "local" in result.stdout
    assert "orphaned" in result.stdout.lower()
    assert "Docker containers" in result.stdout


def test_diagnose_exits_nonzero_on_error_status():
    report = {
        "overall_status": "error",
        "checks": [{"name": "db", "status": "error", "detail": "down"}],
        "proxmox": {},
        "docker": {},
    }
    with patch("apps.cli.main.run_diagnostics", new=AsyncMock(return_value=report)):
        result = runner.invoke(app, ["diagnose"])
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# ai generate: success paths + validation failure (lines 317-342)
# ---------------------------------------------------------------------------


def test_ai_generate_success_prints_yaml():
    with patch(
        "apps.cli.main.generate_blueprint_yaml", new=AsyncMock(return_value=_VALID_BLUEPRINT_YAML)
    ):
        result = runner.invoke(app, ["ai", "generate", "a nginx container"])
    assert result.exit_code == 0
    assert "gen-test" in result.stdout


def test_ai_generate_success_writes_output_file(tmp_path: Path):
    out = tmp_path / "bp.yaml"
    with patch(
        "apps.cli.main.generate_blueprint_yaml", new=AsyncMock(return_value=_VALID_BLUEPRINT_YAML)
    ):
        result = runner.invoke(app, ["ai", "generate", "a nginx container", "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "Blueprint written to" in result.stdout


def test_ai_generate_validation_failure_exits_one():
    invalid_yaml = "not_a_blueprint: true\n"
    with patch("apps.cli.main.generate_blueprint_yaml", new=AsyncMock(return_value=invalid_yaml)):
        result = runner.invoke(app, ["ai", "generate", "bad description"])
    assert result.exit_code == 1
    assert "validation" in result.stdout.lower()


# ---------------------------------------------------------------------------
# proxmox discover: connected path (lines 355-411)
# ---------------------------------------------------------------------------


def test_proxmox_discover_connected_with_all_data():
    report = {
        "connected": True,
        "nodes": [
            {
                "node": "pve",
                "cpu_percent": 5,
                "memory_used_gb": 2,
                "memory_total_gb": 8,
                "disk_used_gb": 10,
                "disk_total_gb": 200,
            }
        ],
        "storage": [
            {"node": "pve", "storage": "local", "type": "dir", "used_gb": 5, "total_gb": 50}
        ],
        "templates": [{"node": "pve", "vmid": 100, "name": "ubuntu-22.04", "kind": "vm"}],
        "networks": [{"node": "pve", "bridge": "vmbr0", "active": True}],
        "existing_resources": ["vm-101", "vm-102"],
    }
    with patch("apps.cli.main.discover_proxmox_environment", new=AsyncMock(return_value=report)):
        result = runner.invoke(app, ["proxmox", "discover"])
    assert result.exit_code == 0
    assert "ubuntu-22.04" in result.stdout
    assert "vmbr0" in result.stdout
    assert "Existing resources: 2" in result.stdout


def test_proxmox_discover_connected_no_templates():
    report = {
        "connected": True,
        "nodes": [],
        "storage": [],
        "templates": [],
        "networks": [],
        "existing_resources": [],
    }
    with patch("apps.cli.main.discover_proxmox_environment", new=AsyncMock(return_value=report)):
        result = runner.invoke(app, ["proxmox", "discover"])
    assert result.exit_code == 0
    assert "No VM/LXC templates found" in result.stdout


# ---------------------------------------------------------------------------
# resource action: node/vmid options, error print, failed exit (lines 428-443)
# ---------------------------------------------------------------------------


def test_resource_action_with_node_and_vmid_prints_error_detail():
    task = _make_task("success", {"error": "minor warning"})
    with patch("apps.cli.main.execute_resource_action", new=AsyncMock(return_value=task)):
        result = runner.invoke(
            app,
            ["resource", "action", "proxmox", "start", "vm-101", "--node", "pve", "--vmid", "101"],
        )
    assert result.exit_code == 0
    assert "minor warning" in result.stdout


def test_resource_action_failed_exits_one():
    task = _make_task("failed", {"error": "connection refused"})
    with patch("apps.cli.main.execute_resource_action", new=AsyncMock(return_value=task)):
        result = runner.invoke(app, ["resource", "action", "proxmox", "start", "vm-101"])
    assert result.exit_code == 1
    assert "connection refused" in result.stdout


# ---------------------------------------------------------------------------
# snapshot create: success + description payload (lines 453, 474)
# ---------------------------------------------------------------------------


def test_snapshot_create_success():
    task = _make_task("success")
    with patch("apps.cli.main.execute_resource_action", new=AsyncMock(return_value=task)):
        result = runner.invoke(
            app,
            ["snapshot", "create", "pve", "101", "snap1", "--description", "before update"],
        )
    assert result.exit_code == 0
    assert "snap1" in result.stdout


# ---------------------------------------------------------------------------
# snapshot list: success paths (lines 489-499)
# ---------------------------------------------------------------------------


def test_snapshot_list_with_snapshots():
    task = _make_task("success", {"snapshots": [{"name": "snap1", "description": "before update"}]})
    with patch("apps.cli.main.execute_resource_action", new=AsyncMock(return_value=task)):
        result = runner.invoke(app, ["snapshot", "list", "pve", "101"])
    assert result.exit_code == 0
    assert "snap1" in result.stdout
    assert "before update" in result.stdout


def test_snapshot_list_empty():
    task = _make_task("success", {"snapshots": []})
    with patch("apps.cli.main.execute_resource_action", new=AsyncMock(return_value=task)):
        result = runner.invoke(app, ["snapshot", "list", "pve", "101"])
    assert result.exit_code == 0
    assert "No snapshots found" in result.stdout


# ---------------------------------------------------------------------------
# snapshot delete: success path (line 520)
# ---------------------------------------------------------------------------


def test_snapshot_delete_success():
    task = _make_task("success")
    with patch("apps.cli.main.execute_resource_action", new=AsyncMock(return_value=task)):
        result = runner.invoke(app, ["snapshot", "delete", "pve", "101", "snap1", "--yes"])
    assert result.exit_code == 0
    assert "deleted" in result.stdout


# ---------------------------------------------------------------------------
# snapshot rollback: confirm no + success (lines 532-543)
# ---------------------------------------------------------------------------


def test_snapshot_rollback_aborts_when_declined():
    result = runner.invoke(app, ["snapshot", "rollback", "pve", "101", "snap1"], input="n\n")
    assert result.exit_code == 0


def test_snapshot_rollback_success():
    task = _make_task("success")
    with patch("apps.cli.main.execute_resource_action", new=AsyncMock(return_value=task)):
        result = runner.invoke(app, ["snapshot", "rollback", "pve", "101", "snap1", "--yes"])
    assert result.exit_code == 0
    assert "snap1" in result.stdout


def test_snapshot_rollback_reports_failure():
    """Lines 541-542: failed rollback task prints error and exits with code 1."""
    task = _make_task("failed", {"error": "rollback failed"})
    with patch("apps.cli.main.execute_resource_action", new=AsyncMock(return_value=task)):
        result = runner.invoke(app, ["snapshot", "rollback", "pve", "101", "snap1", "--yes"])
    assert result.exit_code == 1
    assert "rollback failed" in result.stdout


# ---------------------------------------------------------------------------
# doctor: all-pass, fast mode, gate failure, long output truncation
# ---------------------------------------------------------------------------


def _mock_proc(returncode: int = 0, stdout: str = "", stderr: str = "") -> MagicMock:
    proc = MagicMock()
    proc.returncode = returncode
    proc.stdout = stdout
    proc.stderr = stderr
    return proc


def test_doctor_all_pass():
    with patch("apps.cli.main.subprocess.run", return_value=_mock_proc(0)):
        result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "All gates passed" in result.stdout


def test_doctor_fast_mode_skips_tests():
    calls: list = []

    def _side(cmd: list, **_: object) -> MagicMock:
        calls.append(cmd)
        return _mock_proc(0)

    with patch("apps.cli.main.subprocess.run", side_effect=_side):
        result = runner.invoke(app, ["doctor", "--fast"])

    assert result.exit_code == 0
    assert not any("pytest" in " ".join(c) for c in calls)


def test_doctor_gate_failure_exits_one():
    def _side(cmd: list, **_: object) -> MagicMock:
        failing = "ruff" in " ".join(cmd)
        return _mock_proc(1 if failing else 0, stdout="ruff error output")

    with patch("apps.cli.main.subprocess.run", side_effect=_side):
        result = runner.invoke(app, ["doctor", "--fast"])

    assert result.exit_code == 1
    assert "gate(s) failed" in result.stdout


def test_doctor_long_failure_output_is_truncated():
    long_out = "e" * 200
    with patch("apps.cli.main.subprocess.run", return_value=_mock_proc(1, stdout=long_out)):
        result = runner.invoke(app, ["doctor", "--fast"])

    assert result.exit_code == 1
    assert "e" * 200 not in result.stdout  # full 200-char string must not appear verbatim


def test_doctor_short_failure_output_no_ellipsis():
    with patch("apps.cli.main.subprocess.run", return_value=_mock_proc(1, stdout="short error")):
        result = runner.invoke(app, ["doctor", "--fast"])

    assert result.exit_code == 1
    assert "short error" in result.stdout


# ---------------------------------------------------------------------------
# audit: clean tree, dirty tree, git unavailable
# ---------------------------------------------------------------------------


def _git_mock(branch: str, sha: str, status: str, log: str) -> MagicMock:
    """Return a side-effect function that dispatches git subcommand responses."""

    def _side(cmd: list, **_: object) -> MagicMock:
        if cmd[0] != "git":
            return _mock_proc(0)
        subcmd = cmd[1] if len(cmd) > 1 else ""
        if subcmd == "log":
            return _mock_proc(0, stdout=log)
        if subcmd == "status":
            return _mock_proc(0, stdout=status)
        if "--abbrev-ref" in cmd:
            return _mock_proc(0, stdout=branch)
        if "--short" in cmd:
            return _mock_proc(0, stdout=sha)
        return _mock_proc(0)

    return MagicMock(side_effect=_side)


def test_audit_clean_tree():
    mock = _git_mock("main", "abc1234", "", "abc1234 fix: something")
    with patch("apps.cli.main.subprocess.run", mock):
        result = runner.invoke(app, ["audit"])

    assert result.exit_code == 0
    assert "main" in result.stdout
    assert "clean" in result.stdout
    assert "Recent commits" in result.stdout


def test_audit_dirty_tree():
    mock = _git_mock("feature/x", "def5678", "M readme.md", "")
    with patch("apps.cli.main.subprocess.run", mock):
        result = runner.invoke(app, ["audit"])

    assert result.exit_code == 0
    assert "dirty" in result.stdout


def test_audit_git_unavailable():
    with patch("apps.cli.main.subprocess.run", return_value=_mock_proc(1)):
        result = runner.invoke(app, ["audit"])

    assert result.exit_code == 0
    assert "N/A" in result.stdout


def test_audit_shows_wsl_suffix_when_detected():
    mock = _git_mock("main", "abc1234", "", "")
    wsl_platform = {"system": "Linux", "release": "5.15.0-microsoft-standard", "is_wsl": True}
    with (
        patch("apps.cli.main.subprocess.run", mock),
        patch("apps.cli.main.detect_os_platform", return_value=wsl_platform),
    ):
        result = runner.invoke(app, ["audit"])

    assert result.exit_code == 0
    assert "WSL" in result.stdout


# ---------------------------------------------------------------------------
# CI-001: doctor --json / --quiet / --non-interactive
# ---------------------------------------------------------------------------


def test_doctor_json_output_all_pass():
    with patch("apps.cli.main.subprocess.run", return_value=_mock_proc(0)):
        result = runner.invoke(app, ["doctor", "--fast", "--json"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["failed"] == 0
    assert data["passed"] > 0
    assert all(g["status"] == "pass" for g in data["gates"])
    assert all("name" in g and "detail" in g for g in data["gates"])


def test_doctor_json_output_with_failure():
    def _side(cmd: list, **_: object) -> MagicMock:
        failing = "ruff" in " ".join(cmd)
        return _mock_proc(1 if failing else 0, stdout="ruff: E501 line too long")

    with patch("apps.cli.main.subprocess.run", side_effect=_side):
        result = runner.invoke(app, ["doctor", "--fast", "--json"])

    assert result.exit_code == 1
    data = json.loads(result.stdout)
    assert data["failed"] >= 1
    failed_gates = [g for g in data["gates"] if g["status"] == "fail"]
    assert failed_gates
    assert failed_gates[0]["detail"] != ""


def test_doctor_json_no_rich_markup():
    with patch("apps.cli.main.subprocess.run", return_value=_mock_proc(0)):
        result = runner.invoke(app, ["doctor", "--fast", "--json"])

    assert "[green]" not in result.stdout
    assert "[red]" not in result.stdout


def test_doctor_quiet_suppresses_output_on_pass():
    with patch("apps.cli.main.subprocess.run", return_value=_mock_proc(0)):
        result = runner.invoke(app, ["doctor", "--fast", "--quiet"])

    assert result.exit_code == 0
    assert result.stdout.strip() == ""


def test_doctor_quiet_suppresses_output_on_fail():
    with patch("apps.cli.main.subprocess.run", return_value=_mock_proc(1, stdout="err")):
        result = runner.invoke(app, ["doctor", "--fast", "--quiet"])

    assert result.exit_code == 1
    assert result.stdout.strip() == ""


def test_doctor_non_interactive_behaves_same_as_default():
    with patch("apps.cli.main.subprocess.run", return_value=_mock_proc(0)):
        result = runner.invoke(app, ["doctor", "--fast", "--non-interactive"])

    assert result.exit_code == 0
    assert "All gates passed" in result.stdout


# ---------------------------------------------------------------------------
# CI-001: audit --json / --quiet / --non-interactive
# ---------------------------------------------------------------------------


def test_audit_json_output():
    mock = _git_mock("main", "abc1234", "", "abc1234 fix: something")
    with patch("apps.cli.main.subprocess.run", mock):
        result = runner.invoke(app, ["audit", "--json"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["branch"] == "main"
    assert data["sha"] == "abc1234"
    assert data["working_tree"] == "clean"
    assert isinstance(data["python_files"], int)
    assert isinstance(data["test_files"], int)
    assert isinstance(data["recent_commits"], list)


def test_audit_json_dirty_tree():
    mock = _git_mock("feature/x", "def5678", "M readme.md", "")
    with patch("apps.cli.main.subprocess.run", mock):
        result = runner.invoke(app, ["audit", "--json"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["working_tree"] == "dirty"


def test_audit_quiet_suppresses_output():
    mock = _git_mock("main", "abc1234", "", "")
    with patch("apps.cli.main.subprocess.run", mock):
        result = runner.invoke(app, ["audit", "--quiet"])

    assert result.exit_code == 0
    assert result.stdout.strip() == ""


def test_audit_non_interactive_behaves_same_as_default():
    mock = _git_mock("main", "abc1234", "", "abc1234 feat: init")
    with patch("apps.cli.main.subprocess.run", mock):
        result = runner.invoke(app, ["audit", "--non-interactive"])

    assert result.exit_code == 0
    assert "main" in result.stdout


# ---------------------------------------------------------------------------
# CI-001: diagnose --json / --quiet / --non-interactive
# ---------------------------------------------------------------------------


def test_diagnose_json_output_ok():
    report = {
        "overall_status": "ok",
        "checks": [{"name": "db", "status": "ok", "detail": "alive"}],
        "proxmox": {},
        "docker": {},
    }
    with patch("apps.cli.main.run_diagnostics", new=AsyncMock(return_value=report)):
        result = runner.invoke(app, ["diagnose", "--json"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["overall_status"] == "ok"
    assert "checks" in data


def test_diagnose_json_output_error_exits_one():
    report = {
        "overall_status": "error",
        "checks": [{"name": "db", "status": "error", "detail": "down"}],
        "proxmox": {},
        "docker": {},
    }
    with patch("apps.cli.main.run_diagnostics", new=AsyncMock(return_value=report)):
        result = runner.invoke(app, ["diagnose", "--json"])

    assert result.exit_code == 1
    data = json.loads(result.stdout)
    assert data["overall_status"] == "error"


def test_diagnose_quiet_suppresses_output():
    report = {
        "overall_status": "ok",
        "checks": [],
        "proxmox": {},
        "docker": {},
    }
    with patch("apps.cli.main.run_diagnostics", new=AsyncMock(return_value=report)):
        result = runner.invoke(app, ["diagnose", "--quiet"])

    assert result.exit_code == 0
    assert result.stdout.strip() == ""


def test_diagnose_quiet_error_exits_one_no_output():
    report = {
        "overall_status": "error",
        "checks": [],
        "proxmox": {},
        "docker": {},
    }
    with patch("apps.cli.main.run_diagnostics", new=AsyncMock(return_value=report)):
        result = runner.invoke(app, ["diagnose", "--quiet"])

    assert result.exit_code == 1
    assert result.stdout.strip() == ""


def test_diagnose_non_interactive_behaves_same_as_default():
    report = {
        "overall_status": "ok",
        "runtime_environment": "local",
        "checks": [{"name": "db", "status": "ok", "detail": "alive"}],
        "proxmox": {},
        "docker": {},
    }
    with patch("apps.cli.main.run_diagnostics", new=AsyncMock(return_value=report)):
        result = runner.invoke(app, ["diagnose", "--non-interactive"])

    assert result.exit_code == 0
    assert "overall status" in result.stdout.lower()


def test_diagnose_shows_cloud_provider_when_detected():
    report = {
        "overall_status": "ok",
        "runtime_environment": "container",
        "environment_details": {
            "os_platform": {"system": "Linux", "release": "6.1", "is_wsl": False},
            "cloud_provider": "aws",
        },
        "checks": [{"name": "db", "status": "ok", "detail": "alive"}],
        "proxmox": {},
        "docker": {},
    }
    with patch("apps.cli.main.run_diagnostics", new=AsyncMock(return_value=report)):
        result = runner.invoke(app, ["diagnose"])

    assert result.exit_code == 0
    assert "container (aws)" in result.stdout


# ---------------------------------------------------------------------------
# CI-002: Bandit gate included in doctor; standalone SAST smoke test
# ---------------------------------------------------------------------------


def test_doctor_includes_bandit_gate():
    """Bandit SAST gate must appear in the doctor gate list."""
    calls: list[list[str]] = []

    def _side(cmd: list, **_: object) -> MagicMock:
        calls.append(cmd)
        return _mock_proc(0)

    with patch("apps.cli.main.subprocess.run", side_effect=_side):
        result = runner.invoke(app, ["doctor", "--fast"])

    assert result.exit_code == 0
    gate_cmds = [" ".join(c) for c in calls]
    assert any("bandit" in cmd for cmd in gate_cmds), f"bandit not in gates: {gate_cmds}"


def test_doctor_bandit_failure_propagates():
    """A Bandit finding (non-zero exit) must cause doctor to exit 1."""

    def _side(cmd: list, **_: object) -> MagicMock:
        if "bandit" in " ".join(cmd):
            return _mock_proc(1, stderr="Issue: [B101] assert used")
        return _mock_proc(0)

    with patch("apps.cli.main.subprocess.run", side_effect=_side):
        result = runner.invoke(app, ["doctor", "--fast"])

    assert result.exit_code == 1
    assert "gate(s) failed" in result.stdout


def test_bandit_sast_passes_on_codebase():
    """Bandit -ll must exit 0 against the actual codebase (integration gate)."""
    import subprocess as sp

    proc = sp.run(
        ["uv", "run", "bandit", "-r", "packages/", "apps/", "scripts/", "-ll", "-q"],
        capture_output=True,
        text=True,
    )  # noqa: S603
    assert proc.returncode == 0, f"Bandit found MEDIUM+ issues:\n{proc.stderr}"
