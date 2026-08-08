# CONSOLIDATION ROADMAP

Standard: SPOS-016 §9 | Aktualizováno: 2026-08-08 | Status: 100% DOKONČENO

Chronologický plán konsolidace repozitáře s prioritami a závislostmi.

---

## PRIORITNÍ ŘAZENÍ

```yaml
P0_CRITICAL:  Blokuje CI/CD funkcionalitu
P1_HIGH:      Významně zlepšuje repository hygiene
P2_MEDIUM:    Code quality, dependency cleanup
P3_LOW:       Kosmetické, nice-to-have
```

---

## ROADMAP

### MILESTONE 1 — CI/CD Fix (P0, 1-2h) ✅ DONE (SPOS-017, commit 1b93a0a)

| # | Akce | Priority | Effort | Závislosti |
|---|---|---|---|---|
| M1.1 | Opravit/smazat starcore-integrity.yml | P0 | XS | Žádné |
| M1.2 | Smazat starcore-release.yml | P0 | XS | Žádné |
| M1.3 | Přesunout codeql.yml do root .github/ | P0 | XS | M1.1 |
| M1.4 | Přesunout docker-publish.yml do root .github/ | P0 | XS | M1.1 |
| M1.5 | Přesunout security-nightly.yml do root .github/ | P0 | XS | M1.1 |
| M1.6 | Přesunout dependabot-auto-merge.yml do root .github/ | P0 | XS | M1.1 |
| M1.7 | Smazat 3 duplikátní workflows z platform/.github/ | P0 | XS | M1.3..M1.6 |
| M1.8 | Ověřit CI green | P0 | — | M1.7 |

**Výsledek:** 10/10 aktivních workflows (z 4/13 aktuálních), 0 orphaned, 0 broken

### MILESTONE 2 — Dead Code Removal (P1, 1h) ✅ DONE (SPOS-018, commit 70186bc)

| # | Akce | Priority | Effort | Závislosti |
|---|---|---|---|---|
| M2.1 | Smazat github_intelligence/ | P1 | XS | Žádné |
| M2.2 | Smazat knowledge_engine/ | P1 | XS | Žádné |
| M2.3 | Smazat performance/ | P1 | XS | Žádné |
| M2.4 | Smazat api_gateway/ | P1 | XS | Žádné |
| M2.5 | Smazat registry/ (prázdné JSON) | P1 | XS | Žádné |
| M2.6 | Smazat bin/control-center symlink | P1 | XS | Žádné |
| M2.7 | Smazat/přesunout stale root files | P1 | XS | Žádné |

**Výsledek:** -9 zbytečných položek z root

### MILESTONE 3 — Repository Restructure (P1, 4-6h) ✅ DONE (SPOS-019, commit c3c4924)

| # | Akce | Priority | Effort | Závislosti |
|---|---|---|---|---|
| M3.1 | Vytvořit legacy/ strukturu | P1 | XS | M2 |
| M3.2 | Přesunout Termux dirs + skripty | P1 | S | M3.1 |
| M3.3 | Přesunout legacy version dirs | P1 | S | M3.1 |
| M3.4 | Přesunout generated data | P1 | S | M3.1 |
| M3.5 | Přesunout stale config | P1 | XS | M3.1 |
| M3.6 | Vytvořit legacy/README.md | P1 | XS | M3.2..M3.5 |
| M3.7 | Aktualizovat root .gitignore | P1 | XS | M3.6 |
| M3.8 | Ověřit CI green | P1 | — | M3.7 |

**Výsledek:** Root obsahuje jen 5-7 adresářů místo 35

### MILESTONE 4 — Code Quality (P2, 1-2h) ✅ DONE (SPOS-020, commit 87a0ede)

| # | Akce | Priority | Effort | Závislosti |
|---|---|---|---|---|
| M4.1 | Deduplikovat _persist_run() | P2 | XS | Žádné |
| M4.2 | Odebrat psutil z přímých deps | P2 | XS | Žádné |
| M4.3 | Ověřit CI green (pytest, ruff) | P2 | — | M4.1, M4.2 |

**Výsledek:** 0 code duplicates, clean dependency list

---

## METRIKY PRO TRACKING

| Metrika | Aktuální | Po M1 | Po M2 | Po M3 | Po M4 |
|---|---|---|---|---|---|
| Root dirs | 35 | 35 | 28 | 7 | 7 |
| Active workflows | 4/13 | 10/10 | 10/10 | 10/10 | 10/10 |
| Dead code | 4 dirs | 4 | 0 | 0 | 0 |
| Code duplicates | 1 | 1 | 1 | 1 | 0 |
| Repo hygiene | 35% | 45% | 55% | 85% | 90% |
| Arch alignment | 79% | 85% | 87% | 92% | 95% |
| Tech debt items | 16 | 13 | 7 | 3 | 0 |

---

## IMPLEMENTAČNÍ PRAVIDLA

1. **Vyžádat schválení** před každým destructive krokem (rm, mv, workflow change)
2. **Atomické commity** — jeden commit per milestone krok
3. **CI ověření** po každém milestone
4. **Governance update** po každém push (DIGITAL_TWIN, registries)
5. **Žádné kódové změny** v platform/packages/ mimo M4 (code quality)
6. **Git history** zachována — `git mv` místo rm+add kde možné
