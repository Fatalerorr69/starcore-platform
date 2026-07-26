# Repository Stabilization Runbook

## Scope

This runbook defines the minimum repeatable workflow for maintaining STARCORE Platform after architectural or operational changes.

## Local validation

```bash
uv sync --extra dev
uv run ruff check .
uv run pyright
uv run pytest -q
uv run pre-commit run --all-files
uv run pip-audit
uv run bandit -r packages/ apps/ scripts/ -ll -q
uv run alembic check
```

## Container validation

```bash
docker build -t starcore-platform:validation .
docker run -d --name starcore-validation \
  -p 8000:8000 \
  -e STARCORE_DATABASE_URL=sqlite:////data/starcore.db \
  starcore-platform:validation
curl --fail http://localhost:8000/health

docker logs starcore-validation
docker rm -f starcore-validation
```

## Change workflow

1. Create a branch from `main`.
2. Audit the current state before modifying behavior.
3. Implement one coherent change set.
4. Add or update tests for the behavior changed.
5. Run targeted tests.
6. Run the complete quality gates.
7. Validate packaging and container behavior when relevant.
8. Update current-state documentation.
9. Review the final diff for secrets, accidental files and unrelated changes.
10. Commit using Conventional Commits.
11. Open a pull request for review.

## Rollback

If a change introduces a regression:

1. Stop further deployment.
2. Record the failing commit SHA and validation output.
3. Revert the affected PR or commit on a dedicated rollback branch.
4. Re-run the complete quality and smoke gates.
5. If a database migration is involved, follow the migration-specific rollback procedure rather than deleting or manually editing production data.
6. Document the incident and root cause before reimplementation.

## Operational safety

The Docker socket mount gives the API container privileged control over the Docker host. Treat the API key as equivalent to host administrative credentials for deployments where the Docker provider is enabled. Prefer network isolation, restricted access and a dedicated host or VM for higher-risk deployments.

## Audit artifact

Every significant stabilization cycle should produce a report containing:

- repository commit SHA;
- date/time;
- changed files;
- tests executed and results;
- coverage;
- security scan results;
- packaging result;
- container smoke result;
- unresolved findings;
- rollback notes;
- recommended next actions.
