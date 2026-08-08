# ROOT STRUCTURE POLICY

Standard: SPOS-019 | Datum: 2026-08-08

Defines the canonical root directory structure after SPOS-019 Repository Restructure.

---

## CANONICAL ROOT STRUCTURE

```
starcore-platform/
├── platform/           ← Active platform (Python, v0.6.0)
├── knowledge/          ← Knowledge base (SAKB)
├── legacy/             ← Archived components v6.x-8.x
├── .claude/            ← AI Engineering governance (SES/SAKB/SPOS)
└── .github/            ← CI/CD workflows
```

## RULES

1. **No new root-level directories** without explicit governance approval
2. **No new root-level scripts** — all scripts belong in platform/ or legacy/
3. **knowledge/** stays at root — active SAKB governance role
4. **legacy/** is read-only archive — no new code, no imports
5. **platform/** is the sole active codebase
6. **.claude/** is the governance layer — standards, registries, reports
7. **.github/** is the CI/CD layer — workflows only

## ADDING NEW COMPONENTS

New components must be added to `platform/` (packages, apps, plugins) or `knowledge/` (knowledge base entries). Root-level additions require SPOS governance approval documenting:
- Purpose and scope
- Why it cannot be in platform/ or knowledge/
- Impact on repository hygiene metrics
