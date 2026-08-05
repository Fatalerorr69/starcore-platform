"""
Blueprint Loader

Supports Jinja2 parametrization: {{ var }} expressions in blueprint YAML are
rendered before parsing. Blueprint-level `vars:` provides defaults; override
vars passed to load()/load_from_string() take precedence.

Jinja2 expressions must be quoted in YAML to remain valid YAML syntax:
    cores: "{{ cores }}"     # correct
    cores: {{ cores }}       # invalid YAML — do not use
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml
from jinja2 import StrictUndefined, UndefinedError
from jinja2.sandbox import SandboxedEnvironment

from .models import Blueprint


class BlueprintRenderError(ValueError):
    """Raised when a Jinja2 template variable is referenced but not defined."""


class BlueprintLoader:
    @staticmethod
    def load(path: str | Path, vars: dict[str, Any] | None = None) -> Blueprint:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        return BlueprintLoader._load_from_text(text, vars)

    @staticmethod
    def load_from_string(text: str, vars: dict[str, Any] | None = None) -> Blueprint:
        return BlueprintLoader._load_from_text(text, vars)

    @staticmethod
    def _load_from_text(text: str, override_vars: dict[str, Any] | None = None) -> Blueprint:
        blueprint_vars = BlueprintLoader._extract_vars(text)
        merged = {**blueprint_vars, **(override_vars or {})}
        rendered = BlueprintLoader._render(text, merged)
        data = yaml.safe_load(rendered)
        return Blueprint.model_validate(data)

    @staticmethod
    def _extract_vars(text: str) -> dict[str, Any]:
        """Extract the `vars:` section before Jinja2 rendering.

        Replaces all {{ ... }} expressions with null so the YAML is
        parse-safe for vars extraction even when resources use templates.
        """
        safe = re.sub(r"\{\{.*?\}\}", "null", text, flags=re.DOTALL)
        try:
            raw = yaml.safe_load(safe)
            return raw.get("vars", {}) if isinstance(raw, dict) else {}
        except yaml.YAMLError:
            return {}

    @staticmethod
    def _render(text: str, vars: dict[str, Any]) -> str:
        env = SandboxedEnvironment(undefined=StrictUndefined)
        try:
            return env.from_string(text).render(**vars)
        except UndefinedError as exc:
            raise BlueprintRenderError(f"Undefined blueprint variable: {exc}") from exc
