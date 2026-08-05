# STARCORE Platform

Declarative infrastructure orchestration for Docker and Proxmox homelabs.

STARCORE Platform lets you describe infrastructure (Docker containers,
Proxmox VMs and LXC containers) as YAML blueprints with explicit
dependencies, then plans and executes them safely — sequentially or
concurrently — through a CLI or a FastAPI-based HTTP API.

## Where to go next

- [Installation](installation.md) — get the platform running locally or in
  Docker.
- [Architecture](architecture.md) — how the modular monolith is layered
  (Provider SDK, Blueprint Engine, Orchestrator, Core, CLI).
- [Development](development.md) — quality gates, tests, and the
  contribution workflow.

## Current state vs. vision

This documentation describes the **actual current state** of the codebase.
The long-term vision and engineering specifications live separately in
`docs/ses/` in the repository and describe where the project is headed,
not what exists today. The README's "What Works Today" and "What's
Planned, Not Built Yet" tables are the authoritative summary of that
split.

Per-sprint change history lives in `docs/changelog/`.
