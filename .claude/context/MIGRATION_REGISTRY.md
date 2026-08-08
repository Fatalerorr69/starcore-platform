# MIGRATION REGISTRY

Standard: SPOS-019 | Datum: 2026-08-08

Evidence-based registry of all file/directory migrations performed in SPOS-019.

---

## MIGRATIONS

| ID | Source | Destination | Method | Classification |
|---|---|---|---|---|
| MIG-001 | agents/ | legacy/agents/ | git mv | SAFE_TO_MOVE |
| MIG-002 | ai_core/ | legacy/ai_core/ | git mv | SAFE_TO_MOVE |
| MIG-003 | ai_runtime/ | legacy/ai_runtime/ | git mv | SAFE_TO_MOVE |
| MIG-004 | automation/ | legacy/automation/ | git mv | SAFE_TO_MOVE |
| MIG-005 | autonomous/ | legacy/autonomous/ | git mv | SAFE_TO_MOVE |
| MIG-006 | backups/ | legacy/backups/ | git mv | SAFE_TO_MOVE |
| MIG-007 | bundles_7x/ | legacy/bundles_7x/ | git mv | SAFE_TO_MOVE |
| MIG-008 | cli/ | legacy/cli/ | git mv | SAFE_TO_MOVE |
| MIG-009 | config/ | legacy/config/ | git mv | SAFE_TO_MOVE |
| MIG-010 | control_center/ | legacy/control_center/ | git mv | SAFE_TO_MOVE |
| MIG-011 | core/ | legacy/core/ | git mv | SAFE_TO_MOVE |
| MIG-012 | distributed/ | legacy/distributed/ | git mv | SAFE_TO_MOVE |
| MIG-013 | hardening/ | legacy/hardening/ | git mv | SAFE_TO_MOVE |
| MIG-014 | installers/ | legacy/installers/ | git mv | SAFE_TO_MOVE |
| MIG-015 | intelligence/ | legacy/intelligence/ | git mv | SAFE_TO_MOVE |
| MIG-016 | mission_engine/ | legacy/mission_engine/ | git mv | SAFE_TO_MOVE |
| MIG-017 | plugins/ | legacy/plugins/ | git mv | SAFE_TO_MOVE |
| MIG-018 | prompts/ | legacy/prompts/ | git mv | SAFE_TO_MOVE |
| MIG-019 | runtime/ | legacy/runtime/ | git mv | SAFE_TO_MOVE |
| MIG-020 | sdk/ | legacy/sdk/ | git mv | SAFE_TO_MOVE |
| MIG-021 | security/ | legacy/security/ | git mv | SAFE_TO_MOVE |
| MIG-022 | sessions/ | legacy/sessions/ | git mv | SAFE_TO_MOVE |
| MIG-023 | studio/ | legacy/studio/ | git mv | SAFE_TO_MOVE |
| MIG-024 | templates/ | legacy/templates/ | git mv | SAFE_TO_MOVE |
| MIG-025 | tools/ | legacy/tools/ | git mv | SAFE_TO_MOVE |
| MIG-026 | 68x *.sh scripts | legacy/termux-scripts/ | git mv | TERMUX_LEGACY |
| MIG-KEEP | knowledge/ | (kept at root) | — | KEEP |

## VALIDATION

- 10-point safety check (A-J) applied to every candidate
- 0 platform/ production references found
- 0 CI/workflow references found
- 0 Python import references found
- All `from core.` imports resolve to platform/packages/core/ (pyproject.toml pythonpath)
- Post-migration sweep: no functional broken references

## POLICY

- Reverse migration: `git mv legacy/<dir> <dir>` restores original path with full history
- No new code in legacy/
- No imports from legacy/ modules
- Active development belongs in platform/
