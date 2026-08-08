# REPOSITORY HYGIENE REPORT

Standard: SPOS-018 | Aktualizováno: 2026-08-08

---

## METRIKY

| Metrika | Pred SPOS-018 | Po SPOS-018 | Delta |
|---|---|---|---|
| Root dirs | 35 | 27 | -8 |
| Root files (stale) | 3 | 0 | -3 |
| Orphaned workflows | 0 (fixed by SPOS-017) | 0 | 0 |
| Stub/empty dirs | 6 | 0 | -6 |
| Broken symlinks | 1 | 0 | -1 |
| Repo hygiene score | 65% | 72% | +7% |
| Tech debt items | 13 | 7 | -6 |

## VYRESENE TECH DEBT

| ID | Popis | Status |
|---|---|---|
| TD-011 | bin/control-center broken symlink | RESOLVED |
| TD-012 | requirements.txt redundant | RESOLVED |
| TD-013 | .envrc stale | RESOLVED |
| TD-014 | config.yaml stale | RESOLVED |
| TD-015 | 4 dead code directories | RESOLVED |
| TD-016 | 3 empty registry files | RESOLVED |

## ZBYVAJICI TECH DEBT

| ID | Popis | Priorita |
|---|---|---|
| TD-004 | 24 legacy root directories | HIGH |
| TD-005 | 65 install scripts | HIGH |
| TD-006 | 411 runtime JSON files | HIGH |
| TD-007 | 16MB Gold Master backup | HIGH |
| TD-008 | _persist_run() duplicate | MEDIUM |
| TD-009 | psutil dependency | LOW |
| TD-010 | platform/reports/ stale | LOW |

## QC VYSLEDKY

| Check | Vysledek |
|---|---|
| pytest | 796 passed, 9 skipped |
| ruff check | All checks passed |
| ruff format | 138 files already formatted |
| pyright | 0 errors, 0 warnings |
| mkdocs --strict | Build OK |

## DALSI DOPORUCENY KROK

Milestone 3: Repository Restructure (P1) — presunout 24 legacy dirs do legacy/ subdirectory.
