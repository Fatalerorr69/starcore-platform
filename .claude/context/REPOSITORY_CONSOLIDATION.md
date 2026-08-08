# REPOSITORY CONSOLIDATION

Standard: SPOS-016 §1 | Aktualizováno: 2026-08-08

Hlavní konsolidační dokument — shrnutí stavu, akčních položek a konsolidačního plánu.

---

## EXECUTIVE SUMMARY

STARCORE repozitář obsahuje **35 root-level adresářů**, **73+ root-level souborů**, ale pouze **4 adresáře jsou aktivní** (platform/, .claude/, knowledge/, .github/). Zbylých 31 adresářů a 68+ shell skriptů pochází z předchozích verzí STARCORE (6.x/7.x/8.x) a Termux Android deploymentu.

**Žádný legacy/termux kód není importován platformou.** Platform/ je self-contained modular monolith s 100% test coverage.

---

## KONSOLIDAČNÍ KATEGORIE

### 1. KEEP (4 adresáře + 3 soubory)

| Položka | Důvod |
|---|---|
| `platform/` | Aktivní kódová báze v0.6.0 |
| `.claude/` | SES/SAKB/SPOS governance vrstva |
| `knowledge/` | SAKB knowledge base (technologie, source registry) |
| `.github/workflows/` | CI/CD (po konsolidaci) |
| `README.md` | Root dokumentace |
| `SECURITY.md` | Security policy |
| `.gitignore` | Git configuration |

### 2. MERGE (workflows)

| Zdroj | Cíl | Akce |
|---|---|---|
| `platform/.github/workflows/codeql.yml` | `.github/workflows/codeql.yml` | Přidat working-directory: platform |
| `platform/.github/workflows/docker-publish.yml` | `.github/workflows/docker-publish.yml` | Přidat working-directory kde potřeba |
| `platform/.github/workflows/security-nightly.yml` | `.github/workflows/security-nightly.yml` | Přidat working-directory: platform |
| `platform/.github/workflows/dependabot-auto-merge.yml` | `.github/workflows/dependabot-auto-merge.yml` | Kopírovat přímo |
| `platform/.github/workflows/ci.yml` | — | SMAZAT (duplikát root ci.yml) |
| `platform/.github/workflows/release.yml` | — | SMAZAT (duplikát root release.yml) |
| `platform/.github/workflows/manual-tag.yml` | — | SMAZAT (duplikát root manual-tag.yml) |

### 3. ARCHIVE (24 dirs + 68 scripts)

Všechny legacy/termux adresáře a install skripty přesunout do `legacy/` subdirectory:

```
legacy/
├── v6x/                    ← STARCORE 6.x kód
│   ├── core/
│   └── ...
├── v7x/                    ← STARCORE 7.x kód
│   ├── control_center/
│   ├── mission_engine/
│   ├── studio/
│   ├── sdk/
│   ├── bundles_7x/
│   └── ...
├── v8x/                    ← STARCORE 8.x kód
│   ├── hardening/
│   ├── installers/
│   └── ...
├── termux/                 ← Termux-specific
│   ├── agents/
│   ├── ai_core/
│   ├── ai_runtime/
│   ├── autonomous/
│   ├── distributed/
│   ├── plugins/
│   ├── tools/
│   ├── runtime/
│   └── install_*.sh (65 skriptů)
├── config/                 ← Stale konfigurace
│   ├── config.yaml
│   ├── .envrc
│   └── requirements.txt
└── README.md               ← Vysvětlení legacy adresáře
```

### 4. REMOVE (5 dirs + 3 files)

| Položka | Důvod |
|---|---|
| `github_intelligence/` | Dead code, zero references |
| `knowledge_engine/` | Dead code, zero references |
| `performance/` | Dead code, zero references |
| `api_gateway/` | Dead code, zero references |
| `registry/` | Prázdné JSON soubory |
| `starcore-integrity.yml` | BROKEN workflow (nebo opravit) |
| `starcore-release.yml` | LEGACY workflow (jen git status) |
| Root `starcore` | Termux entry point |

### 5. FIX (code + config)

| Položka | Akce | Effort |
|---|---|---|
| `_persist_run()` duplicate | Extrahovat do sdíleného modulu | XS |
| `psutil` v pyproject.toml | Odebrat z přímých deps | XS |
| `bin/control-center` | Smazat broken symlink | XS |

---

## KONSOLIDAČNÍ FÁZE

### Fáze 1: Quick Wins (XS, 2-3h)

1. Smazat 4 dead code dirs
2. Smazat 3 prázdné registry
3. Smazat broken symlink bin/control-center
4. Smazat/opravit starcore-integrity.yml
5. Smazat starcore-release.yml
6. Odebrat psutil z přímých deps (pokud potvrzeno testy)

### Fáze 2: Workflow Consolidation (S, 2-3h)

1. Přesunout codeql.yml, docker-publish.yml, security-nightly.yml, dependabot-auto-merge.yml do root .github/workflows/
2. Smazat duplikátní workflows z platform/.github/
3. Ověřit CI green

### Fáze 3: Repository Restructure (M, 4-6h)

1. Vytvořit legacy/ adresář
2. Přesunout 24 legacy/termux dirs + 65 install scripts
3. Přesunout stale config files
4. Aktualizovat .gitignore
5. Ověřit CI green

### Fáze 4: Code Quality (XS, 1h)

1. Deduplikovat _persist_run()
2. Vyčistit psutil dependency

---

## METRIKY PŘED/PO KONSOLIDACI

| Metrika | Před | Po (projektované) |
|---|---|---|
| Root dirs | 35 | 7 (platform, .claude, knowledge, .github, legacy, .git) |
| Root files | 73+ | 5 (README, SECURITY, .gitignore, .gitattributes) |
| Active workflows | 4/13 | 10/10 |
| Broken workflows | 2 | 0 |
| Dead code dirs | 4 | 0 |
| Repository hygiene | 35% | 85%+ |
| Architecture alignment | 79% | 92%+ |

---

## RIZIKA KONSOLIDACE

| Riziko | Pravděpodobnost | Dopad | Mitigace |
|---|---|---|---|
| Legacy kód potřebný v budoucnu | LOW | MEDIUM | Git history zachovává, legacy/ tag |
| CI break při přesunu workflows | MEDIUM | HIGH | Testovat v PR, ne na main |
| Import paths break | NONE | — | platform/ je self-contained, root dirs nejsou importovány |
| Ztráta runtime state | LOW | LOW | runtime/ je generovaný, regenerovatelný |
