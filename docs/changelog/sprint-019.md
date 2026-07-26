# Sprint 019 — CHANGELOG Unreleased Section, `_resolve_request_id` Property Tests

**Date:** 2026-07-26
**Branch:** `claude/new-session-b47q19`
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### A — `CHANGELOG.md`: add `## [Unreleased]` section
`release.yml`'s "Extract release notes from CHANGELOG.md" step requires a
`## [VERSION]` entry matching the pushed git tag. Only `## [0.1.0]` existed
(covering sprints 001-015); sprint-016 through sprint-018 (dependency
failure semantics enforcement / ADR-010, centralized secret redaction,
plugin trust boundary / ADR-011, API auth model / ADR-012, provider
concurrency policy / ADR-013, CodeQL, Docker multi-stage build, request
correlation IDs, snapshot rollback dry-run diff, docker-compose scaffold
fix, release.yml gate parity, new reference docs) were undocumented there —
tagging a new version today would have hit "no release notes found" in CI.

Added an `## [Unreleased]` section (standard Keep a Changelog convention,
which the file already declares it follows) summarizing everything shipped
since 0.1.0, grouped Fixed/Added/Changed to match the existing 0.1.0 entry's
style. `pyproject.toml`'s version was deliberately left untouched — cutting
a new release is the maintainer's call, not something to decide as a
documentation fix. Verified `release.yml`'s extraction `awk` command still
correctly isolates the `[0.1.0]` section with the new section preceding it.

### B — Property-based tests for `_resolve_request_id()`
`packages/core/main.py`'s `_resolve_request_id()` (X-Request-ID validation:
echo a caller-supplied token matching `^[A-Za-z0-9_-]{1,128}$`, else
generate a UUID4) had only deterministic unit tests. Added 3 Hypothesis
tests to `test_property_based_core.py`:

| Test | Invariant |
|------|-----------|
| `test_resolve_request_id_echoes_valid_token_unchanged` | Any token matching the allowed pattern is returned exactly as given |
| `test_resolve_request_id_generates_valid_uuid4_for_invalid_input` | Any non-matching input (including `None`) produces a valid, parseable UUID4 |
| `test_resolve_request_id_rejects_tokens_over_128_chars` | A 129+ character token is rejected even if every character is otherwise valid |

## Test counts
| Before | After |
|--------|-------|
| 493 passed | 496 passed |
| 100% coverage | 100% coverage |
