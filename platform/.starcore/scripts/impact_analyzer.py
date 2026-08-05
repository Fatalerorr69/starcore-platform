#!/usr/bin/env python3
"""
STARCORE Change Impact Analyzer CLI.

Maps changed files to their impact scope using actual repository evidence
(git diff + grep). Never generates speculative impact lists.

Použití:
  uv run python .starcore/scripts/impact_analyzer.py analyze
  uv run python .starcore/scripts/impact_analyzer.py analyze --since HEAD~1
  uv run python .starcore/scripts/impact_analyzer.py analyze --files packages/core/main.py
  uv run python .starcore/scripts/impact_analyzer.py module packages/orchestrator/timeout.py
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

_SCRIPT_DIR = Path(__file__).parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent

sys.path.insert(0, str(_SCRIPT_DIR))
from models import CheckResult, CheckState  # noqa: E402

# ── Path → module mapping (most specific first) ───────────────────────────────

_PATH_MODULE_MAP: list[tuple[str, str]] = [
    ("packages/core/main.py", "core.main"),
    ("packages/core/config.py", "core.config"),
    ("packages/core/database.py", "core.database"),
    ("packages/core/models_db.py", "core.models_db"),
    ("packages/core/security.py", "core.security"),
    ("packages/core/metrics.py", "core.metrics"),
    ("packages/core/events.py", "core.events"),
    ("packages/core/correlation.py", "core.correlation"),
    ("packages/core/environment.py", "core.environment"),
    ("packages/core/plugin_manager.py", "core.plugin_manager"),
    ("packages/core/", "core"),
    ("packages/orchestrator/timeout.py", "orchestrator.timeout"),
    ("packages/orchestrator/scheduler.py", "orchestrator.scheduler"),
    ("packages/orchestrator/task_graph.py", "orchestrator.task_graph"),
    ("packages/orchestrator/task.py", "orchestrator.task"),
    ("packages/orchestrator/", "orchestrator"),
    ("packages/blueprints/executor.py", "blueprints.executor"),
    ("packages/blueprints/planner.py", "blueprints.planner"),
    ("packages/blueprints/loader.py", "blueprints.loader"),
    ("packages/blueprints/models.py", "blueprints.models"),
    ("packages/blueprints/template_resolver.py", "blueprints.template_resolver"),
    ("packages/blueprints/", "blueprints"),
    ("packages/provider_sdk/base.py", "provider_sdk.base"),
    ("packages/provider_sdk/registry.py", "provider_sdk.registry"),
    ("packages/provider_sdk/retry.py", "provider_sdk.retry"),
    ("packages/provider_sdk/exceptions.py", "provider_sdk.exceptions"),
    ("packages/provider_sdk/", "provider_sdk"),
    ("packages/providers/docker/", "providers.docker"),
    ("packages/providers/proxmox/", "providers.proxmox"),
    ("packages/providers/", "providers"),
    ("packages/ai/providers/anthropic.py", "ai.anthropic"),
    ("packages/ai/providers/openai_compat.py", "ai.openai_compat"),
    ("packages/ai/generator.py", "ai.generator"),
    ("packages/ai/base.py", "ai.base"),
    ("packages/ai/prompts.py", "ai.prompts"),
    ("packages/ai/", "ai"),
    ("apps/cli/main.py", "cli.main"),
    ("apps/cli/", "cli"),
    ("tests/", "tests"),
    (".github/workflows/", "ci"),
    ("migrations/", "migrations"),
    ("docs/adr/", "docs.adr"),
    ("docs/", "docs"),
    ("plugins/", "plugins"),
    (".starcore/scripts/", "starcore.scripts"),
    (".starcore/", "starcore"),
    ("pyproject.toml", "packaging"),
    ("Dockerfile", "build"),
    ("docker-compose.yml", "deployment"),
    ("CLAUDE.md", "governance"),
    ("mkdocs.yml", "docs.config"),
]

# ── Impact category inference ─────────────────────────────────────────────────

# Which impact categories each module tag triggers
_MODULE_CATEGORIES: dict[str, list[str]] = {
    "core.main": ["API"],
    "core.config": ["API", "CLI", "CONFIGURATION"],
    "core.database": ["DATABASE", "DEPLOYMENT"],
    "core.models_db": ["DATABASE", "API"],
    "core.security": ["API", "SECURITY"],
    "core.metrics": ["API"],
    "core.events": ["API"],
    "core.correlation": ["API"],
    "core.environment": ["API", "CLI"],
    "core.plugin_manager": ["API", "PLUGINS"],
    "core": ["API", "CLI"],
    "orchestrator.timeout": ["RECOVERY"],
    "orchestrator.scheduler": ["DEPLOYMENT", "RECOVERY"],
    "orchestrator.task_graph": [],
    "orchestrator.task": [],
    "orchestrator": [],
    "blueprints.executor": ["CLI", "API"],
    "blueprints.planner": ["CLI", "API"],
    "blueprints": [],
    "provider_sdk.base": ["API", "CLI", "DEPLOYMENT", "RECOVERY"],
    "provider_sdk.registry": ["API", "CLI"],
    "provider_sdk.retry": ["RECOVERY"],
    "provider_sdk": ["API", "CLI"],
    "providers.docker": ["DEPLOYMENT", "RECOVERY"],
    "providers.proxmox": ["DEPLOYMENT", "RECOVERY"],
    "providers": ["DEPLOYMENT"],
    "ai": ["API", "CLI"],
    "cli.main": ["CLI"],
    "cli": ["CLI"],
    "tests": [],
    "ci": ["CI"],
    "migrations": ["DATABASE", "DEPLOYMENT"],
    "docs.adr": ["DOCUMENTATION", "GOVERNANCE"],
    "docs": ["DOCUMENTATION"],
    "packaging": ["PACKAGE", "DEPLOYMENT", "CI"],
    "build": ["BUILD", "DEPLOYMENT", "CI"],
    "deployment": ["DEPLOYMENT"],
    "governance": ["DOCUMENTATION", "GOVERNANCE"],
    "docs.config": ["DOCUMENTATION", "CI"],
    "plugins": [],
    "starcore": [],
    "starcore.scripts": [],
}


def path_to_module(file_path: str) -> str:
    """Map a repo-relative file path to its module identifier."""
    # Normalise separators
    fp = file_path.replace("\\", "/")
    for prefix, module in _PATH_MODULE_MAP:
        if fp == prefix or fp.startswith(prefix):
            return module
    return "unknown"


def module_to_impact_categories(module: str) -> list[str]:
    """Return impact categories for a module (exact match then prefix)."""
    if module in _MODULE_CATEGORIES:
        return _MODULE_CATEGORIES[module]
    for key, cats in _MODULE_CATEGORIES.items():
        if module.startswith(key + ".") or module.startswith(key):
            return cats
    return []


# ── Evidence gathering ────────────────────────────────────────────────────────


def _run(cmd: list[str], cwd: Path | None = None) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd or _REPO_ROOT))
    return r.stdout.strip()


def get_changed_files(since: str | None, files: list[str] | None) -> list[str]:
    """Return repo-relative list of changed files from git or explicit list."""
    if files:
        return [f.strip() for f in files if f.strip()]
    if since:
        out = _run(["git", "diff", "--name-only", since, "HEAD"])
    else:
        # staged + unstaged + untracked (new files)
        staged = _run(["git", "diff", "--staged", "--name-only"])
        unstaged = _run(["git", "diff", "--name-only"])
        out = "\n".join(filter(None, [staged, unstaged]))
    return sorted(set(f for f in out.splitlines() if f))


def find_dependents(module_base: str) -> list[str]:
    """
    Grep packages/ apps/ tests/ for files that import module_base.
    Returns repo-relative paths, deduplicated.
    """
    if not module_base or module_base in ("tests", "ci", "docs", "starcore"):
        return []
    cmd = [
        "grep",
        "-rl",
        f"from {module_base}",
        "packages/",
        "apps/",
        "tests/",
    ]
    out = _run(cmd)
    if not out:
        return []
    files = [f for f in out.splitlines() if f and "__pycache__" not in f]
    return sorted(set(files))


def find_test_files(module: str, file_path: str) -> list[str]:
    """Find test files that directly reference the changed file or module."""
    stem = Path(file_path).stem  # e.g. "timeout" from "timeout.py"
    base = module.split(".")[-1]  # e.g. "timeout" from "orchestrator.timeout"

    candidates = set()
    tests_dir = _REPO_ROOT / "tests"
    for pattern in [f"test_{stem}.py", f"test_{base}.py"]:
        p = tests_dir / pattern
        if p.exists():
            candidates.add(f"tests/{p.name}")

    # Also grep tests/ for any reference to the module's import path
    for search in set([stem, base]):
        out = _run(["grep", "-rl", search, "tests/"])
        for f in out.splitlines():
            if f and "__pycache__" not in f:
                candidates.add(f)

    return sorted(candidates)


# ── Impact record ─────────────────────────────────────────────────────────────


@dataclass
class FileImpact:
    file: str
    module: str
    categories: list[str]
    dependents: list[str]
    test_files: list[str]

    def to_lines(self) -> list[str]:
        lines = [f"  FILE        : {self.file}"]
        lines.append(f"  MODULE      : {self.module}")
        lines.append(f"  CATEGORIES  : {', '.join(self.categories) if self.categories else '—'}")
        if self.dependents:
            lines.append(f"  DEPENDENTS  : {len(self.dependents)} soubor(ů)")
            lines.extend(f"                {d}" for d in self.dependents[:5])
            if len(self.dependents) > 5:
                lines.append(f"                … a {len(self.dependents) - 5} dalších")
        else:
            lines.append("  DEPENDENTS  : —")
        if self.test_files:
            lines.append(f"  TESTS       : {', '.join(self.test_files[:4])}")
        else:
            lines.append("  TESTS       : —")
        return lines


def analyze_file(file_path: str) -> FileImpact:
    module = path_to_module(file_path)
    categories = module_to_impact_categories(module)
    module_base = module.split(".")[0]
    dependents = find_dependents(module_base)
    test_files = find_test_files(module, file_path)
    return FileImpact(
        file=file_path,
        module=module,
        categories=categories,
        dependents=dependents,
        test_files=test_files,
    )


def summarize_impacts(impacts: list[FileImpact]) -> CheckResult:
    """Roll up a list of FileImpact into a single CheckResult."""
    all_cats: set[str] = set()
    for imp in impacts:
        all_cats.update(imp.categories)

    critical = {"API", "CLI", "DEPLOYMENT", "SECURITY", "DATABASE"}
    hit_critical = all_cats & critical

    if hit_critical:
        state = CheckState.WARNING
        detail = f"Změny zasahují kritické oblasti: {', '.join(sorted(hit_critical))}"
    elif all_cats:
        state = CheckState.PASS
        detail = f"Dopad: {', '.join(sorted(all_cats))}"
    else:
        state = CheckState.PASS
        detail = "Dopad omezen na interní/testovací/dokumentační soubory"

    evidence = [f"{imp.file} → {imp.module}" for imp in impacts]
    return CheckResult(name="change_impact", state=state, detail=detail, evidence=evidence)


# ── CLI commands ──────────────────────────────────────────────────────────────

_SEP = "─" * 72


def cmd_analyze(args: argparse.Namespace) -> int:
    files_arg = getattr(args, "files", None) or []
    changed = get_changed_files(
        since=getattr(args, "since", None),
        files=files_arg,
    )

    if not changed:
        print("Žádné změněné soubory nenalezeny.")
        return 0

    print(f"\n{_SEP}")
    print(f"STARCORE Change Impact Analyzer — {len(changed)} soubor(ů)")
    print(_SEP)

    impacts: list[FileImpact] = []
    for f in changed:
        imp = analyze_file(f)
        impacts.append(imp)
        for line in imp.to_lines():
            print(line)
        print()

    summary = summarize_impacts(impacts)
    print(_SEP)
    print(f"SOUHRN: {summary.icon} {summary.state}  —  {summary.detail}")
    print(_SEP)
    return 0 if summary.state != CheckState.FAIL else 1


def cmd_module(args: argparse.Namespace) -> int:
    module = path_to_module(args.file_path)
    cats = module_to_impact_categories(module)
    print(f"file   : {args.file_path}")
    print(f"module : {module}")
    print(f"impact : {', '.join(cats) if cats else '—'}")
    return 0


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="impact_analyzer",
        description="STARCORE Change Impact Analyzer",
    )
    sub = parser.add_subparsers(dest="command")

    p_analyze = sub.add_parser("analyze", help="Analyzovat dopad změněných souborů")
    p_analyze.add_argument(
        "--since",
        default=None,
        metavar="COMMIT",
        help="Porovnat s tímto commitem (výchozí: pracovní strom)",
    )
    p_analyze.add_argument("--files", nargs="+", metavar="FILE", help="Explicitní seznam souborů")

    p_mod = sub.add_parser("module", help="Zjistit modul pro soubor")
    p_mod.add_argument("file_path", help="Cesta k souboru (relativní k repozitáři)")

    args = parser.parse_args()
    dispatch = {"analyze": cmd_analyze, "module": cmd_module}

    if args.command not in dispatch:
        parser.print_help()
        return 1
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
