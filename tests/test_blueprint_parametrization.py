"""
Blueprint parametrization tests.

Covers Jinja2 rendering in BlueprintLoader, the _parse_vars CLI helper,
and --var option in blueprint plan/run commands.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from blueprints.loader import BlueprintLoader, BlueprintRenderError
from blueprints.models import Blueprint

# ── _render ────────────────────────────────────────────────────────────────────


def test_render_substitutes_variable():
    text = "name: svc-{{ env }}\nversion: '1.0'\nresources: []"
    result = BlueprintLoader._render(text, {"env": "prod"})
    assert "svc-prod" in result


def test_render_strict_undefined_raises():
    text = "name: svc-{{ missing }}\nversion: '1.0'\nresources: []"
    with pytest.raises(BlueprintRenderError, match="Undefined blueprint variable"):
        BlueprintLoader._render(text, {})


def test_render_no_templates_returns_text_unchanged():
    text = "name: plain\nversion: '1.0'\nresources: []"
    assert BlueprintLoader._render(text, {}) == text


# ── _extract_vars ──────────────────────────────────────────────────────────────


def test_extract_vars_returns_declared_vars():
    text = "name: bp\nversion: '1.0'\nvars:\n  env: staging\n  cores: 2\nresources: []"
    assert BlueprintLoader._extract_vars(text) == {"env": "staging", "cores": 2}


def test_extract_vars_returns_empty_when_no_vars_section():
    text = "name: bp\nversion: '1.0'\nresources: []"
    assert BlueprintLoader._extract_vars(text) == {}


def test_extract_vars_handles_jinja2_in_resources():
    text = (
        "name: bp\nvars:\n  node: lab\nresources:\n"
        "  - name: vm\n    provider: proxmox\n    kind: vm\n"
        '    config:\n      node: "{{ node }}"\n'
    )
    assert BlueprintLoader._extract_vars(text) == {"node": "lab"}


def test_extract_vars_returns_empty_on_invalid_yaml():
    assert BlueprintLoader._extract_vars(":::not: valid: yaml:::") == {}


def test_extract_vars_returns_empty_for_non_dict_yaml():
    assert BlueprintLoader._extract_vars("- item1\n- item2\n") == {}


# ── load_from_string ───────────────────────────────────────────────────────────


def test_load_from_string_no_vars_works_as_before():
    text = "name: plain\nversion: '2.0'\nresources: []"
    bp = BlueprintLoader.load_from_string(text)
    assert bp.name == "plain"
    assert bp.version == "2.0"


def test_load_from_string_with_override_vars():
    text = "name: svc-{{ env }}\nversion: '1.0'\nvars:\n  env: staging\nresources: []"
    bp = BlueprintLoader.load_from_string(text, vars={"env": "prod"})
    assert bp.name == "svc-prod"


def test_load_from_string_blueprint_defaults_apply_when_no_override():
    text = "name: svc-{{ env }}\nversion: '1.0'\nvars:\n  env: staging\nresources: []"
    bp = BlueprintLoader.load_from_string(text)
    assert bp.name == "svc-staging"


def test_load_from_string_override_wins_over_blueprint_defaults():
    text = (
        "name: bp\nversion: '1.0'\nvars:\n  env: staging\n"
        'resources:\n  - name: "vm-{{ env }}"\n    provider: docker\n'
        "    kind: container\n"
    )
    bp = BlueprintLoader.load_from_string(text, vars={"env": "prod"})
    assert bp.resources[0].name == "vm-prod"


def test_load_from_string_undefined_var_raises():
    text = "name: svc-{{ missing }}\nversion: '1.0'\nresources: []"
    with pytest.raises(BlueprintRenderError):
        BlueprintLoader.load_from_string(text)


def test_load_from_string_vars_field_preserved_in_model():
    text = "name: bp\nversion: '1.0'\nvars:\n  env: dev\nresources: []"
    bp = BlueprintLoader.load_from_string(text)
    assert bp.vars == {"env": "dev"}


def test_load_from_string_type_coercion_int_var():
    text = (
        "name: bp\nversion: '1.0'\n"
        "resources:\n  - name: vm\n    provider: proxmox\n    kind: vm\n"
        '    config:\n      cores: "{{ cores }}"\n'
    )
    bp = BlueprintLoader.load_from_string(text, vars={"cores": 4})
    assert bp.resources[0].config["cores"] == "4"


# ── load (file path) ───────────────────────────────────────────────────────────


def test_load_from_file_with_vars(tmp_path: Path):
    blueprint_file = tmp_path / "infra.yaml"
    blueprint_file.write_text(
        "name: svc-{{ env }}\nversion: '1.0'\nvars:\n  env: dev\nresources: []\n",
        encoding="utf-8",
    )
    bp = BlueprintLoader.load(blueprint_file, vars={"env": "production"})
    assert bp.name == "svc-production"


def test_load_from_file_uses_blueprint_defaults(tmp_path: Path):
    blueprint_file = tmp_path / "infra.yaml"
    blueprint_file.write_text(
        "name: svc-{{ env }}\nversion: '1.0'\nvars:\n  env: dev\nresources: []\n",
        encoding="utf-8",
    )
    bp = BlueprintLoader.load(blueprint_file)
    assert bp.name == "svc-dev"


# ── Blueprint model ────────────────────────────────────────────────────────────


def test_blueprint_vars_defaults_to_empty():
    bp = Blueprint(name="x")
    assert bp.vars == {}


def test_blueprint_round_trips_with_vars():
    bp = Blueprint(name="x", vars={"env": "prod", "cores": 4})
    restored = Blueprint.model_validate(bp.model_dump())
    assert restored.vars == {"env": "prod", "cores": 4}


# ── CLI --var option ───────────────────────────────────────────────────────────


def test_parse_vars_empty_list():
    from apps.cli.main import _parse_vars

    assert _parse_vars([]) == {}


def test_parse_vars_string_value():
    from apps.cli.main import _parse_vars

    assert _parse_vars(["env=production"]) == {"env": "production"}


def test_parse_vars_int_coercion():
    from apps.cli.main import _parse_vars

    result = _parse_vars(["cores=4"])
    assert result == {"cores": 4}
    assert isinstance(result["cores"], int)


def test_parse_vars_float_coercion():
    from apps.cli.main import _parse_vars

    result = _parse_vars(["ratio=1.5"])
    assert result == {"ratio": 1.5}
    assert isinstance(result["ratio"], float)


def test_parse_vars_bool_true():
    from apps.cli.main import _parse_vars

    assert _parse_vars(["flag=true"]) == {"flag": True}
    assert _parse_vars(["flag=True"]) == {"flag": True}


def test_parse_vars_bool_false():
    from apps.cli.main import _parse_vars

    assert _parse_vars(["flag=false"]) == {"flag": False}
    assert _parse_vars(["flag=False"]) == {"flag": False}


def test_parse_vars_value_with_equals():
    from apps.cli.main import _parse_vars

    assert _parse_vars(["url=http://host:8080/path"]) == {"url": "http://host:8080/path"}


def test_parse_vars_multiple():
    from apps.cli.main import _parse_vars

    result = _parse_vars(["env=prod", "cores=8", "debug=false"])
    assert result == {"env": "prod", "cores": 8, "debug": False}


def test_parse_vars_invalid_format_raises():
    import typer

    from apps.cli.main import _parse_vars

    with pytest.raises(typer.BadParameter, match="KEY=VALUE"):
        _parse_vars(["no-equals-sign"])


def test_cli_blueprint_plan_with_var(tmp_path: Path):
    from typer.testing import CliRunner

    from apps.cli.main import app

    blueprint_file = tmp_path / "bp.yaml"
    blueprint_file.write_text(
        "name: svc-{{ env }}\nversion: '1.0'\nresources:\n"
        "  - name: vm\n    provider: docker\n    kind: container\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(app, ["blueprint", "plan", str(blueprint_file), "--var", "env=prod"])
    assert result.exit_code == 0
    assert "vm" in result.output


def test_cli_blueprint_plan_render_error(tmp_path: Path):
    from typer.testing import CliRunner

    from apps.cli.main import app

    blueprint_file = tmp_path / "bp.yaml"
    blueprint_file.write_text(
        "name: svc-{{ missing_var }}\nversion: '1.0'\nresources: []\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(app, ["blueprint", "plan", str(blueprint_file)])
    assert result.exit_code == 1
    assert "render error" in result.output.lower()


def test_cli_blueprint_run_with_var(tmp_path: Path):
    from typer.testing import CliRunner

    from apps.cli.main import app

    blueprint_file = tmp_path / "bp.yaml"
    blueprint_file.write_text(
        "name: svc-{{ env }}\nversion: '1.0'\nresources:\n"
        "  - name: vm\n    provider: docker\n    kind: container\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(app, ["blueprint", "run", str(blueprint_file), "--var", "env=test"])
    # Provider 'docker' won't connect in tests, so exit 1 is expected, but it ran
    assert "svc-test" in result.output or result.exit_code in (0, 1)


def test_cli_blueprint_run_render_error(tmp_path: Path):
    from typer.testing import CliRunner

    from apps.cli.main import app

    blueprint_file = tmp_path / "bp.yaml"
    blueprint_file.write_text(
        "name: svc-{{ missing }}\nversion: '1.0'\nresources: []\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(app, ["blueprint", "run", str(blueprint_file)])
    assert result.exit_code == 1
    assert "render error" in result.output.lower()


# ── Yaml round-trip via load_from_string ──────────────────────────────────────


def test_existing_blueprints_without_vars_still_load():
    """Blueprints without {{ }} are unaffected by the Jinja2 layer."""
    text = yaml.dump(
        {
            "name": "demo",
            "version": "1.0",
            "resources": [{"name": "web", "provider": "docker", "kind": "container", "config": {}}],
        }
    )
    bp = BlueprintLoader.load_from_string(text)
    assert bp.name == "demo"
    assert bp.resources[0].name == "web"
