# ADR-008 — CI Security Gates: Bandit, gitleaks, and Nightly Audit

**Date:** 2026-07-25
**Status:** Accepted
**Deciders:** Core team

---

## Context

Before PR #78, CI's only security-relevant gate was `pip-audit` (ADR-004),
which scans the locked dependency graph for known CVEs. It says nothing
about vulnerabilities *introduced* in this repository's own code (insecure
patterns like `subprocess` with `shell=True`, weak crypto, hardcoded
binds) or about secrets accidentally committed (API keys, tokens).

## Decision

Add two further blocking checks to the `CI/quality` job, plus a nightly
workflow that reruns the full security stack independent of any PR:

- **Bandit SAST** (`uv run bandit -r packages/ apps/ scripts/ -ll -q`) —
  static analysis for insecure Python patterns. Run at `-ll` (medium+
  severity only); low-severity findings (e.g. `B101 assert_used`, expected
  throughout the test suite and in a few defensive checks) don't fail CI,
  keeping the gate meaningful rather than noisy.
- **gitleaks** (`gitleaks/gitleaks-action@v2`) — scans the full commit
  history for secrets on every PR and push to `main`. `.gitleaks.toml`
  extends the default ruleset and allowlists three known-safe strings
  (`test-api-key`, `sk-test-key`, `change-me-to-a-random-secret`) that are
  test fixtures or `.env.example` placeholders, not real leaked credentials.
- **`security-nightly.yml`** — reruns `pip-audit`, Bandit, and gitleaks daily
  at 02:00 UTC (plus manual `workflow_dispatch`), independent of PR activity.
  Catches a newly published CVE or a newly added Bandit/gitleaks rule against
  code that already merged, without waiting for the next PR to surface it.

Together with `pip-audit`, the CI security stack covers three distinct
threat surfaces: known-vulnerable dependencies, insecure code patterns
written in this repository, and accidentally committed secrets.

## Consequences

**Positive**
- A merge is blocked on all three surfaces, not just dependency CVEs.
- The nightly run means dependency/rule drift is caught within 24 hours
  even on a quiet repository with no open PRs.
- `scripts/doctor.py` and `starcore doctor` mirror the same gates locally,
  so a contributor can reproduce a CI security failure without pushing.

**Negative / Trade-offs**
- Three additional CI steps increase per-PR run time.
- Bandit's `-ll` threshold is a judgment call: it accepts low-severity
  findings library-wide rather than requiring per-line `# nosec` suppression
  for things like `assert` in test code — a stricter `-l` threshold would
  catch more but at a much higher noise cost for this codebase's test-heavy
  composition.
- gitleaks scans full history on every run; a large future history could
  make this step slower over time (not yet a concern at this repository's
  size).

## Alternatives considered

- **Trivy** for combined dependency + secret + IaC scanning: broader scope
  than needed here, and its container/OS-layer scanning overlaps with
  container-hardening concerns that are out of scope for this ADR (see
  ADR-004's rejection of Trivy for the same reason).
- **Bandit at `-l` (low+ severity)**: rejected — would fail CI on every
  `assert` statement in the test suite, which is standard pytest usage, not
  a real risk; `-ll` keeps the gate signal-to-noise ratio high.
- **Pre-commit-only secret scanning** (no CI step): rejected — pre-commit
  hooks are opt-in locally and can be bypassed with `--no-verify`; a CI gate
  is required to actually block a merge.
