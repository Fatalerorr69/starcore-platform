# ADR-025 — STARCORE Change Governance Lifecycle

- **Status:** Proposed
- **Date:** 2026-08-06
- **Relates to:** ADR-018 through ADR-024 (formalizes the process that produced them)

## Context

ADR-018 through ADR-024 were produced through a consistent but until-now
undocumented sequence: a discovery audit surfaced a problem, a governance
report proposed decisions, the repository owner approved or amended them,
and only then were files written — in staged checkpoints, each step
explicitly labeled SAFE AUTOMATIC, REQUIRE REVIEW, or REQUIRE USER
APPROVAL, with commit and push treated as separate, later-gated actions.

That sequence worked, and was stress-tested in practice: an automated
stop hook repeatedly requested a push of an already-approved commit, and
was correctly not treated as owner approval each time; an ADR draft was
revised only once an explicit, concrete patch specification was supplied,
and was left unchanged when a referenced "review proposal" turned out to
contain no actual content. Without codifying the process, the next
architectural change — or the next bootstrap-style prompt proposing a new
"framework" — has no standing process to point to, and risks re-deriving
the same safeguards inconsistently, or skipping them under pressure
(including pressure from automated tooling, not just from a requester).

## Options

1. **No formal lifecycle** — treat this session's process as one-off;
   future sessions improvise their own review discipline each time.
2. **Codify the lifecycle as an ADR**, naming its stages and the approval
   discipline observed in this session — including explicit controls for
   change classification, discovery grounding, repository integrity,
   knowledge synchronization, release safety, and rollback — so future
   architectural changes reuse it by reference instead of reinvention.
3. **Codify it outside the ADR system** — e.g. as a `.starcore/memory/`
   process document rather than a numbered ADR.

## Decision

**Option 2.** Every architectural change to STARCORE follows this
lifecycle:

```
REQUEST → DISCOVERY → ADR → PLAN → IMPLEMENT → VALIDATE → RELEASE → KNOWLEDGE UPDATE
```

- **REQUEST** — a need is stated, by the repository owner or surfaced by
  an audit finding.
- **DISCOVERY** — read-only analysis of current state; no files change;
  produces a report, not a decision. Governed by the Discovery First
  Principle below.
- **ADR** — the decision is drafted and shown for review *before* being
  written to disk, unless its content has already been approved verbatim
  in a prior step (in which case writing it is SAFE AUTOMATIC per the
  Change Classification Matrix below).
- **PLAN** — a concrete file list, exact commit order, a risk label per
  step, and a stated rollback path (Rollback Requirement below) are
  produced before any write.
- **IMPLEMENT** — executed strictly in the labeled checkpoints, stopping
  at every REQUIRE REVIEW or REQUIRE USER APPROVAL gate for explicit,
  affirmative confirmation.
- **VALIDATE** — the relevant quality gates (CI-equivalent checks such as
  `mkdocs build --strict`, Regression Sentinel, test suite) are run and
  their actual result reported before any commit, per the Repository
  Integrity Gate below.
- **RELEASE** — commit and push are distinct, separately-approved actions,
  governed by the Release Safety Gate below.
- **KNOWLEDGE UPDATE** — mandatory, per the Knowledge Synchronization
  Obligation below; not an optional epilogue.

### Change Classification Matrix

| Change type | Example | Default risk label | Required gate(s) |
|---|---|---|---|
| Documentation, content pre-approved verbatim | Writing an ADR whose exact text the owner already approved | SAFE AUTOMATIC | VALIDATE only |
| Documentation, new/unapproved content | An ADR or ROADMAP draft not yet seen by the owner | REQUIRE REVIEW | ADR/PLAN shown before write |
| Configuration or metadata | `mkdocs.yml` nav, `prompts/registry.yaml` append | REQUIRE REVIEW | diff shown before apply |
| New code, isolated from CI-gated packages | `.starcore/scripts/*.py` | REQUIRE REVIEW | VALIDATE (its own tests) before commit |
| Code inside CI-gated `packages/`/`apps/` | provider, API, CLI change | REQUIRE REVIEW | full CI gate (ruff, pyright, bandit, pytest 100%, alembic check, mkdocs --strict) |
| Baseline/state mutation | `regression_baseline.json` update | REQUIRE USER APPROVAL | only after confirmed CI pass |
| Git commit | any of the above once approved | inherits the item's label | Repository Integrity Gate |
| Git push, force-push, `reset --hard`, branch deletion | any RELEASE to shared history | REQUIRE USER APPROVAL, always | Release Safety Gate — never inferred from automated signals |

### Discovery First Principle

No ADR or decision proceeds without a preceding DISCOVERY step grounded in
actual repository evidence — file reads, `git log`, test runs, direct
inspection — never in assumption, in the requester's framing alone, or in
a prior session's unverified claim. Every factual assertion in a discovery
report must be traceable to a specific command or file (as demonstrated in
the STARCORE SAEF Integration Discovery Report's use of `git log --oneline
--all -- <path>` and direct file reads to substantiate every classification).

### Repository Integrity Gate

Before any RELEASE (commit or push), verify and show:

- `git status` matches exactly the file set defined in PLAN — no
  unrelated staged files, nothing missing.
- `git diff` (or the new-file content, for untracked additions) reviewed
  in full for anything not explicitly approved.
- No secret/credential pattern present, consistent with the repository's
  existing gitleaks CI gate.
- Everything outside the approved file set remains untouched.

This gate is run and its result shown before every commit — it is a
demonstrated step, not an assumed one.

### Knowledge Synchronization Obligation

Every completed RELEASE step is followed by a KNOWLEDGE UPDATE in the same
session, or is explicitly deferred with a stated reason:
`.starcore/memory/completed_work.md`, `sessions/ledger.yaml`, and
`prompts/registry.yaml` must come to reflect the change before the
lifecycle is considered closed. A RELEASE without a corresponding
KNOWLEDGE UPDATE is incomplete, not merely "pending."

### Release Safety Gate

Push, force-push, `reset --hard`, branch deletion, and any other
irreversible or shared-state-affecting git action require a fresh,
explicit, affirmative instruction from the repository owner naming the
action, given in direct response to a specific request for that approval.
Automated environment signals — stop hooks, CI notifications, reminders,
elapsed time, repetition — never satisfy this gate, regardless of how many
times they recur. This formalizes behavior already demonstrated
repeatedly in this session: a stop hook requesting push was acknowledged
but not acted upon, three separate times, because none of those
notifications originated from the repository owner.

### Rollback Requirement

No RELEASE step is approved for execution without a stated, verified
rollback path:

- Local, unpushed commit → `git reset --soft HEAD~N`.
- Pushed commit → `git revert <sha>` — never `reset --hard` or a force-push
  on shared history.
- Baseline/state file mutation → the prior version is retained/diffable
  until the new baseline is confirmed stable.

The rollback path is stated in the PLAN step itself, before
implementation — not improvised after the fact once something has already
gone wrong.

## Consequences

- Future sessions handling an architectural change point to this ADR
  ("per ADR-025") instead of negotiating process from scratch.
- The Change Classification Matrix gives a default risk label for common
  change shapes, reducing ambiguity about what needs review versus what
  can proceed automatically.
- The Release Safety Gate makes explicit and permanent a behavior this
  session already had to apply under real pressure (repeated automated
  push requests); it is no longer implicit convention but a documented
  requirement future sessions are held to.
- The Knowledge Synchronization Obligation prevents a class of drift this
  repository has already experienced once — a real, functioning knowledge
  system (`.starcore/`) coexisting with stale or absent records of what
  actually happened.
- No new tooling is introduced; this ADR names and fixes a sequence and a
  set of controls already demonstrated, it does not require building
  anything.

## Alternatives rejected

**Option 1** was rejected because the original discovery audit exists
specifically because prior sessions had no standing process, which
produced the parallel-framework and undocumented-scaffolding problems
ADR-018 through ADR-024 now correct. Leaving the fix itself unformalized
would repeat the pattern one level up.

**Option 3** was rejected because this lifecycle governs the same class of
decision every other ADR governs — a durable, binding architectural
choice — and belongs in the same numbered, indexed, Regression-Sentinel-
tracked series (`docs/adr/`) as ADR-001 through ADR-024, not in a
separate, less-visible memory file. `.starcore/memory/` remains the right
place for session-local working notes, not for a decision meant to bind
future sessions the way an ADR does.
