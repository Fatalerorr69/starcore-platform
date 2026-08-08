# LEGACY MIGRATION PLAN

Standard: SPOS-016 §2 | Aktualizováno: 2026-08-08

Plán migrace legacy obsahu — přesun, archivace nebo odstranění neaktivních komponent.

---

## STRATEGIE

Legacy obsah se nepřepisuje ani nemigruje na novou architekturu — je příliš rozsáhlý (400+ souborů) a nemá produkční hodnotu. Strategie je **archivace in-place** (přesun do `legacy/` subdirectory) s dokumentovaným původem, aby git history zůstala navigovatelná.

---

## WAVE 1 — REMOVE (okamžité, zero risk)

| # | Akce | Položky | Effort |
|---|---|---|---|
| R1 | Smazat dead code dirs | github_intelligence/, knowledge_engine/, performance/, api_gateway/ | XS |
| R2 | Smazat prázdné registry | registry/modules.json, registry/sdk_registry.json | XS |
| R3 | Smazat broken assets | bin/control-center (broken symlink) | XS |
| R4 | Smazat/opravit broken workflows | starcore-integrity.yml, starcore-release.yml | XS |

**Prerekvizity:** Žádné. Zero cross-references potvrzeno grep auditem.

---

## WAVE 2 — WORKFLOW CONSOLIDATION

| # | Akce | Zdroj → Cíl |
|---|---|---|
| W1 | Přesunout | platform/.github/workflows/codeql.yml → .github/workflows/codeql.yml |
| W2 | Přesunout | platform/.github/workflows/docker-publish.yml → .github/workflows/docker-publish.yml |
| W3 | Přesunout | platform/.github/workflows/security-nightly.yml → .github/workflows/security-nightly.yml |
| W4 | Přesunout | platform/.github/workflows/dependabot-auto-merge.yml → .github/workflows/dependabot-auto-merge.yml |
| W5 | Smazat duplikát | platform/.github/workflows/ci.yml |
| W6 | Smazat duplikát | platform/.github/workflows/release.yml |
| W7 | Smazat duplikát | platform/.github/workflows/manual-tag.yml |

**Úpravy při přesunu:**
- Přidat `defaults: run: working-directory: platform` kde chybí
- Aktualizovat checkout actions na pinned SHAs (match root ci.yml pattern)
- Ověřit trigger conditions (branches, tags)

---

## WAVE 3 — ARCHIVE LEGACY

Přesunout do `legacy/` subdirectory:

```bash
mkdir -p legacy/termux legacy/v6x legacy/v7x legacy/v8x legacy/config legacy/data

# Termux
mv agents/ ai_core/ ai_runtime/ autonomous/ distributed/ tools/ legacy/termux/
mv plugins/ legacy/termux/plugins/
mv install_*.sh generate_*.sh preflight_*.sh repair_*.sh legacy/termux/
mv starcore legacy/termux/

# Legacy versions
mv core/ legacy/v6x/
mv control_center/ bundles_7x/ mission_engine/ studio/ sdk/ cli/ sessions/ templates/ legacy/v7x/
mv hardening/ installers/ legacy/v8x/

# Generated state
mv runtime/ intelligence/ legacy/data/
mv backups/ legacy/data/

# Stale config
mv config/ config.yaml .envrc requirements.txt legacy/config/
mv security/ automation/ prompts/ bin/ legacy/v7x/
```

**Prerekvizity:** Wave 1 a Wave 2 dokončeny. CI green.

---

## WAVE 4 — CODE QUALITY (platform/)

| # | Akce | Soubory | Effort |
|---|---|---|---|
| C1 | Deduplikovat _persist_run() | blueprints.py, ws.py | XS |
| C2 | Odebrat psutil z deps | pyproject.toml | XS |
| C3 | Archivovat stale reports | platform/reports/ → legacy/ | XS |

---

## RIZIKA A MITIGACE

| Riziko | Mitigace |
|---|---|
| Git blame break po mv | `git log --follow` sleduje přesuny |
| CI break | Testovat v PR na branch, ne přímo na main |
| Potřeba starého kódu | Git history zachovává vše, legacy/ tag před smazáním |
| Import paths | platform/ je self-contained — zero cross-references potvrzeno |

---

## TIMELINE

| Wave | Effort | Prerekvizity | Popis |
|---|---|---|---|
| Wave 1 (REMOVE) | XS (1h) | Žádné | Smazat dead/broken/empty |
| Wave 2 (WORKFLOWS) | S (2-3h) | Wave 1 | Konsolidovat CI/CD |
| Wave 3 (ARCHIVE) | M (4-6h) | Wave 2 | Přesunout legacy do legacy/ |
| Wave 4 (CODE) | XS (1h) | Wave 1 | Code quality fixes |

**Celkový odhad: 8-11h** (rozloženo do několika sessions)
