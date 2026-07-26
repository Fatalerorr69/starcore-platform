# STARCORE Platform – GitHub Copilot & Claude Integration Guide

## Overview
This document defines best practices and guidelines for using GitHub Copilot and Claude AI to develop STARCORE Platform.

## Architecture Principles

### 1. **Modular Monolith Pattern**
- **CLI**: `apps/cli/main.py` – Typer-based command interface
- **API**: `packages/core/main.py` – FastAPI server with authentication
- **Domain Packages**: Shared business logic
  - `packages/blueprints/` – YAML parsing, planning, execution
  - `packages/orchestrator/` – Task scheduling, dependency resolution
  - `packages/provider_sdk/` – Abstract provider interface
  - `packages/providers/` – Docker, Proxmox implementations
  - `packages/ai/` – LLM-powered blueprint generation

### 2. **Provider Pattern**
All infrastructure providers must extend `BaseProvider`:
```python
class BaseProvider(ABC):
    async def connect(self) -> bool       # Establish connection (with _connect_lock)
    async def disconnect(self) -> None    # Cleanup
    async def health(self) -> dict        # Provider health status
    async def list_resources(self) -> list[dict]  # Enumerate managed resources
    async def execute(self, task) -> None  # Execute orchestration task
```

**Key Invariants:**
- All methods are `async` (no sync blocking I/O)
- `_connect_lock` must be acquired before mutating connection state (concurrent safety)
- `execute()` must set `task.status` and `task.result`
- Exceptions in `execute()` should not crash the process (caught by executor)

### 3. **Async-First Execution Model**
- Use `asyncio` for concurrency, never threads
- Request correlation via `asyncio.contextvars` (auto-propagated across awaits)
- Event bus (`core.events.event_bus`) for cross-module signaling

### 4. **Dependency Success Gates** (ADR-010)
- `depends_on` is a **success gate**, not just an ordering constraint
- A task only reaches `provider.execute()` if all dependencies have `TaskStatus.SUCCESS`
- If any dependency fails: `task.status = TaskStatus.SKIPPED_DEPENDENCY_FAILED`
- Applied identically in sequential (`BlueprintExecutor`) and parallel (`Scheduler`) paths

### 5. **Event-Driven Architecture**
All major lifecycle events emit to `event_bus`:
- `task.started` – Task entered RUNNING state
- `task.completed` – Task reached terminal state (SUCCESS/FAILED/SKIPPED)
- `run.completed` – Entire blueprint run finished
- Subscribers: plugins can hook into `register(context)` → `context.events.subscribe(...)`

## Coding Standards

### 1. **Type Hints (Python 3.12)**
- **Mandatory**: All function signatures, return types, variable annotations
- Use `|` for unions: `str | None` (PEP 604)
- Use `Annotated[int, Query(...)]` for FastAPI path/query parameters
- Pyright configuration: `pyrightconfig.json` (checked on every PR)

### 2. **Docstrings**
- Public APIs: Google-style docstrings with Args, Returns, Raises sections
- Private methods: Single-line comments suffice
- Example:
```python
async def create_plan(self, blueprint: Blueprint) -> list[dict]:
    """Create execution plan from blueprint with topological sort.
    
    Args:
        blueprint: Blueprint model with resources and dependencies.
    
    Returns:
        List of execution steps in dependency order.
    
    Raises:
        CyclicDependencyError: If blueprint contains dependency cycle.
    """
```

### 3. **Testing (100% Coverage Floor)**
- **Unit Tests**: `tests/test_*.py` – Test individual functions
- **Integration Tests**: `tests/integration/` – Multi-component flows
- **Property-Based Tests**: Use Hypothesis for state machines (e.g., TaskGraph)
- **Fixtures**: Centralized in `tests/conftest.py`
- **Coverage**: `uv run pytest --cov --cov-fail-under=100` (non-negotiable)

### 4. **Security**
- **No Secrets in Code**: Use `STARCORE_*` environment variables (via Pydantic Settings)
- **Bandit SAST**: `uv run bandit -r packages/ apps/ scripts/ -ll -q` (medium+ severity)
- **gitleaks**: Scan on every PR (`gitleaks/gitleaks-action@v2`)
- **Constant-Time Comparison**: Use `hmac.compare_digest()` for API key validation

### 5. **Error Handling**
- Raise `ProviderException` (or subclass) for provider-level errors
- Log exceptions with context: `logger.exception("Failed to execute task for '{}'", resource_name)`
- Never suppress exceptions silently
- Use specific exception types (not bare `Exception`)

### 6. **Code Style**
- **Linting**: Ruff (`ruff.toml` defines rules)
- **Formatting**: Ruff formatter
- **Pre-commit Hooks**: `.pre-commit-config.yaml` auto-checks on commit
- **Command**: `uv run ruff check . && uv run ruff format .`

## File Organization

### Top-Level Directories
```
starcore-platform/
├── apps/
│   └── cli/
│       ├── main.py              # Typer app, all CLI commands
│       ├── utils/               # CLI-specific helpers
│       └── __init__.py
├── packages/
│   ├── core/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Pydantic Settings
│   │   ├── database.py          # SQLAlchemy engine, session factory
│   │   ├── models_db.py         # ORM models (Base.metadata)
│   │   ├── logger.py            # loguru setup (JSON logging)
│   │   ├── metrics.py           # Prometheus collectors
│   │   ├── events.py            # Event bus singleton
│   │   ├── plugin_manager.py    # Plugin discovery & loading
│   │   ├── diagnostics.py       # Health checks, provider status
│   │   ├── repository.py        # Data access (run history)
│   │   ├── resource_actions.py  # Single-resource lifecycle
│   │   └── static/              # Web UI (HTML/JS)
│   ├── blueprints/
│   │   ├── models.py            # Blueprint, Resource, Task models
│   │   ├── loader.py            # YAML parsing & validation
│   │   ├── planner.py           # Execution plan, topological sort
│   │   ├── executor.py          # Sequential blueprint execution
│   │   └── template_resolver.py # Template variable substitution
│   ├── orchestrator/
│   │   ├── task.py              # Task model, TaskStatus enum
│   │   ├── scheduler.py         # Parallel wave executor
│   │   └── task_graph.py        # DAG for dependency tracking
│   ├── provider_sdk/
│   │   ├── base.py              # BaseProvider ABC
│   │   ├── registry.py          # ProviderRegistry singleton
│   │   ├── exceptions.py        # ProviderException hierarchy
│   │   └── __init__.py
│   ├── providers/
│   │   ├── docker/
│   │   │   ├── provider.py      # DockerProvider implementation
│   │   │   └── __init__.py
│   │   ├── proxmox/
│   │   │   ├── provider.py      # ProxmoxProvider implementation
│   │   │   └── __init__.py
│   │   └── __init__.py
│   └── ai/
│       ├── generator.py         # LLM blueprint generation
│       └── __init__.py
├── plugins/
│   ├── example_provider/        # Template plugin
│   │   └── __init__.py
│   └── run_logger/              # Event subscriber example
│       └── __init__.py
├── scripts/
│   ├── setup-copilot.sh         # Copilot integration automation
│   ├── verify-integration.sh    # Verify setup
│   ├── doctor.py                # Health check script
│   └── __init__.py
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_*.py                # Unit tests
│   └── integration/             # Integration tests
├── migrations/
│   ├── env.py                   # Alembic runtime
│   ├── script.py.mako           # Migration template
│   └── versions/                # Individual migrations
├── docs/
│   ├── ses/                     # Long-term engineering spec
│   ├── adr/                     # Architectural decision records
│   ├── copilot-workflow.md      # This guide
│   ├── testing-with-copilot.md  # Testing guidelines
│   └── ENHANCEMENTS.md          # Recent improvements
├── .claude/
│   ├── instructions.md          # (This file)
│   ├── commands/
│   │   └── setup-copilot.sh
│   ├── launch.json              # Debug config
│   └── settings.json            # Claude/Copilot config
├── .vscode/
│   ├── settings.json            # VS Code settings
│   ├── extensions.json          # Recommended extensions
│   └── launch.json              # Debug launcher
├── .github/
│   ├── workflows/
│   │   ├── ci.yml               # Main quality gate
│   │   ├── release.yml          # Release automation
│   │   ├── docker-publish.yml   # Container build & push
│   │   ├── codeql.yml           # Security scanning
│   │   └── security-nightly.yml # Scheduled security audit
│   ├── dependabot.yml           # Dependency updates
│   └── pull_request_template.md # PR template
├── pyproject.toml               # Project metadata, dependencies
├── ruff.toml                    # Ruff configuration
├── pyrightconfig.json           # Pyright configuration
├── Makefile                     # Development targets
├── Dockerfile                   # Container image
├── docker-compose.yml           # Multi-container setup
├── alembic.ini                  # Alembic configuration
└── README.md                    # Project overview
```

## Copilot Usage Patterns

### 1. **Inline Code Completion**
- Start typing a function signature → Copilot suggests implementation
- Accept with `Tab`, reject with `Esc`
- **Best for**: Repetitive patterns, boilerplate

### 2. **Copilot Chat** (Ctrl+L in VS Code/PyCharm)
```
💬 "Write a provider that connects to AWS Lambda"
💬 "Generate a unit test for circular dependency detection"
💬 "Explain the ADR-010 success gate pattern"
💬 "Refactor this async function to use asyncio.gather()"
💬 "Create a migration that adds a 'timeout_seconds' column"
```

### 3. **Commit Message Generation**
```bash
# GitHub CLI
gh copilot suggest "git commit message"

# Or: Let Copilot suggest from diff
git diff | gh copilot suggest
```

### 4. **PR Description Generation**
- Create PR draft → Copilot auto-fills description
- Edit, review, submit

### 5. **Documentation Generation**
```
💬 "Write docstring for ExecutionPlanner.create_plan()"
💬 "Generate API reference for POST /blueprints/run"
💬 "Create ADR for task timeout support"
```

## Quality Gates (Pre-Commit & CI)

### Local (Before Push)
```bash
make lint        # ruff check .
make format      # ruff format .
make test        # pytest -q --cov --cov-fail-under=100
make health      # Full doctor + security scan
```

### CI (GitHub Actions)
1. **Lockfile consistency** – `uv lock --check`
2. **Linting** – `ruff check .`
3. **Type checking** – `pyright`
4. **Security scan** – `pip-audit`, `bandit`, `gitleaks`
5. **Tests** – `pytest` with 100% coverage
6. **Database** – `alembic check` (schema consistency)
7. **Documentation** – `mkdocs build --strict`
8. **Docker** – Build & smoke test container health

## Best Practices for AI-Assisted Development

### Do's ✅
- **Use Copilot for boilerplate** – Tests, type annotations, docstrings
- **Ask specific questions** – "Generate Hypothesis property test for..."
- **Review generated code** – Never auto-accept without understanding
- **Iterate** – "Refactor to use asyncio.gather()" → Review → "Add type hints"
- **Test thoroughly** – Generated code may have edge cases
- **Document decisions** – Use ADRs for non-obvious choices

### Don'ts ❌
- **Don't copy-paste without review** – Understand what you're accepting
- **Don't skip type hints** – Copilot should respect `pyright` settings
- **Don't ignore test failures** – 100% coverage is mandatory
- **Don't commit without `make lint`** – Pre-commit hooks catch this
- **Don't trust external API calls** – Always handle exceptions

## Integration Checklist

- [ ] Install GitHub Copilot extension
- [ ] Create `.vscode/settings.json` (provided)
- [ ] Run `bash scripts/setup-copilot.sh`
- [ ] Verify with `bash scripts/verify-integration.sh`
- [ ] Enable Copilot Chat in IDE (Ctrl+L)
- [ ] Create PR with `[copilot]` label for AI review
- [ ] Review Copilot suggestions in PR comments

## Resources

- [GitHub Copilot Docs](https://docs.github.com/en/copilot)
- [STARCORE ADRs](./adr/)
- [STARCORE SES](./ses/)
- [Copilot Workflow Guide](./copilot-workflow.md)

---

**Last Updated**: 2026-07-26  
**Maintained By**: STARCORE Development Team
