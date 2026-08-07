# ECOSYSTEM MAP

Standard: SPOS-015 §3 | Aktualizováno: 2026-08-07

Definitivní mapa celého STARCORE repozitáře. Každý root-level adresář klasifikován jako ACTIVE, LEGACY, STUB, DEAD nebo EMPTY.

---

## KLASIFIKACE

```yaml
ACTIVE:   Živý kód používaný v produkčním/dev workflow
LEGACY:   Historický kód z dřívějších verzí (6.x/7.x/8.x), nepoužívaný platformou
STUB:     Placeholder (Termux JSON print nebo ~/STARCORE path)
DEAD:     Kód bez jakéhokoli importu/reference odkudkoli
EMPTY:    Registr nebo struktura s prázdným obsahem
GOVERNANCE: .claude/ governance vrstva (SES/SAKB/SPOS)
BUILD:    Build artifact (generováno, ne commitováno)
```

---

## ROOT-LEVEL ADRESÁŘE

```
starcore-platform/
├── .claude/                 GOVERNANCE    SES/SAKB/SPOS governance layer
├── .github/                 ACTIVE        CI workflows (ci.yml, codeql.yml, release.yml, ...)
├── platform/                ACTIVE        Živý monolith (FastAPI + Typer CLI, v0.6.0)
│
├── knowledge/               ACTIVE        SAKB knowledge base (technology profiles, sources)
│   ├── core/                STUB          knowledge_core.py (JSON print)
│   ├── rag/                 STUB          rag_engine.py (JSON print)
│   ├── registry/            ACTIVE        source_registry.yaml
│   └── technologies/        ACTIVE        6 technology profiles
│
├── agents/                  STUB          4 JSON print stubs (SPOS-014 AGENT-S01..S04)
├── ai_core/                 STUB          ai_kernel.py (JSON print)
├── ai_runtime/              STUB          3 Termux stubs (SPOS-014 AGENT-S05..S07)
├── autonomous/              STUB          9 Termux stubs (SPOS-014 AGENT-S08..S16)
├── distributed/             STUB          9 Termux stubs (SPOS-014 AGENT-S17..S25)
│
├── core/                    LEGACY        43 .py souborů, 12 subdirs — legacy Python package
├── control_center/          LEGACY        21 souborů, 4 subdirs — legacy control center
├── mission_engine/          LEGACY        3 soubory — execution/missions/workflows
├── studio/                  LEGACY        3 soubory — dashboard/module_control/system_view
├── sdk/                     LEGACY        4 soubory — core/ subdir
├── hardening/               LEGACY        2 soubory — dependencies + environment audit
├── cli/                     LEGACY        starcore/ CLI package (předchůdce platform/apps/cli/)
├── config/                  LEGACY        5 JSON/YAML config souborů
├── bin/                     LEGACY        3 executable + 1 broken Termux symlink
├── plugins/                 LEGACY        enabled/ + registry/ (ne platform/plugins/)
├── sessions/                LEGACY        session_memory.json
├── prompts/                 LEGACY        3 markdown prompts + generated/
├── backups/                 LEGACY        releases/ subdir
├── installers/              LEGACY        android/ subdir
├── templates/               LEGACY        module_template/ subdir
│
├── tools/                   STUB          18 Termux shell script stubs
├── registry/                EMPTY         modules.json (prázdný), sdk_registry.json (prázdný)
├── runtime/                 MIXED         marketplace/registry.json (prázdný) + jiné
│
├── security/                LEGACY        3 standalone .py skripty (neimportované)
├── intelligence/            LEGACY        —
├── automation/              LEGACY        —
├── github_intelligence/     DEAD          github_scanner.py (zero references)
├── knowledge_engine/        DEAD          knowledge_core.py (zero references)
├── performance/             DEAD          performance_analyzer.py (zero references)
├── api_gateway/             DEAD          api_gateway.py (zero references)
│
├── bundles_7x/              LEGACY        5 batch install shell skriptů
├── install_*.sh (64+)       LEGACY        Termux install skripty (SPOS-008 katalogizováno)
├── docker-compose.yml       ACTIVE        Docker Compose scaffold (postgres, redis, nats)
├── README.md                ACTIVE        Root README
└── .gitignore               ACTIVE        —
```

---

## STATISTIKY

```yaml
total_root_directories: 35+
classification:
  ACTIVE: 4 (platform/, .claude/, .github/, knowledge/)
  GOVERNANCE: 1 (.claude/)
  LEGACY: 18 (core/, control_center/, mission_engine/, studio/, sdk/, hardening/, cli/, config/, bin/, plugins/, sessions/, prompts/, backups/, installers/, templates/, security/, intelligence/, automation/)
  STUB: 5 (agents/, ai_core/, ai_runtime/, autonomous/, distributed/)
  DEAD: 4 (github_intelligence/, knowledge_engine/, performance/, api_gateway/)
  EMPTY: 1 (registry/)
  MIXED: 2 (runtime/, tools/)
```

---

## PLATFORM/ MAPA (ACTIVE)

```
platform/
├── apps/
│   └── cli/                 ACTIVE    Typer CLI (main.py)
├── packages/
│   ├── ai/                  ACTIVE    AI provider abstraction + generator
│   ├── blueprints/          ACTIVE    YAML blueprint loader + planner + executor
│   ├── core/                ACTIVE    FastAPI app, config, DB, events, metrics, security
│   ├── orchestrator/        ACTIVE    Scheduler, TaskGraph, timeout
│   ├── provider_sdk/        ACTIVE    BaseProvider ABC, ProviderRegistry, retry
│   └── providers/           ACTIVE    docker/, proxmox/, kubernetes/
├── plugins/                 ACTIVE    example_provider/, run_logger/
├── tests/                   ACTIVE    796 tests, 100% coverage
├── migrations/              ACTIVE    Alembic (0001, 0002)
├── docs/                    ACTIVE    MkDocs documentation (56 souborů)
├── .starcore/               ACTIVE    Project memory + QC engines
├── scripts/                 PARTIAL   7 souborů (3 nedokumentované)
├── data/                    RUNTIME   starcore.db (SQLite, gitignored pattern)
├── reports/                 LEGACY    12 historických reportů
└── site/                    BUILD     MkDocs generated output
```

---

## VERZE EVOLUCE

```
STARCORE 6.x → install_6B*.sh skripty, core/ package, control_center/
STARCORE 7.x → install_7_*.sh, bundles_7x/, studio/, mission_engine/, sdk/
STARCORE 8.x → install_8*.sh, platform/ (FastAPI monolith — aktuální)
```

Živý kód je výhradně v `platform/` (v0.6.0). Vše ostatní mimo `.claude/` a `knowledge/` je legacy z předchozích verzí.

---

## HEALTH MATRIX

| Vrstva | Adresářů | Souborů | Klasifikace | Governance |
|---|---|---|---|---|
| Active (platform/) | 1 | 200+ | ACTIVE | PLNĚ POKRYTO (SPOS-001..014) |
| Governance (.claude/) | 1 | 100+ | GOVERNANCE | PLNĚ POKRYTO |
| Knowledge | 1 | 20+ | ACTIVE/STUB | ČÁSTEČNĚ (SAKB-000) |
| Stubs | 5 | 25 | STUB | POKRYTO (SPOS-014) |
| Legacy | 18 | 100+ | LEGACY | ❌ NEPOKRYTO |
| Dead | 4 | 5 | DEAD | ❌ NEPOKRYTO |
| Empty | 1 | 2 | EMPTY | ❌ NEPOKRYTO |
