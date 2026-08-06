# SPOS-000 — STARCORE PROJECT OPERATING SYSTEM BOOTSTRAP

```yaml
Document ID:     SPOS-000
Title:           STARCORE Project Operating System — Runtime Bootstrap
Version:         1.0.0
Status:          ACTIVE — APPROVED (existing runtime formally adopted)
Parent:          SES-000, SES-001, SAKB-000
Repository:      Fatalerorr69/starcore-platform
Branch:          claude/starcore-ai-bootstrap-fkyb96
Date Created:    2026-08-06
```

---

## KLÍČOVÉ ZJIŠTĚNÍ (PHASE 1 — DISCOVERY)

Před vytvořením čehokoli nového byl proveden audit existující struktury dle **SES-000 P001 (Architecture First)**.

**Nález:** `.starcore/` runtime vrstva **již existuje** — nikoli na rootu repozitáře, ale v `platform/.starcore/`. Jedná se o plně funkční, netriviální systém:

```
platform/.starcore/
├── README.md            (cold-start protokol, CLI reference)
├── memory/               (9 souborů: project_snapshot, risks, decisions, pending_work, completed_work,
│                          architecture, known_issues, user_preferences, qc_engines, decision_engine)
├── sessions/             (current.md, ledger.yaml, archive/)
├── prompts/              (registry.yaml, master/, audits/, implementation/, recovery/)
├── reports/              (latest/, archive/)
├── scripts/              (3843 řádků Python: models, registry, ledger, decision_engine,
│                          impact_analyzer, regression_sentinel, release_readiness, qc_engine,
│                          startup_protocol + 171 testů)
└── state/                (regression_baseline.json, release.md)
```

Ověřeno **funkčním testem** (`startup_protocol.py --quick --json`) — systém korektně detekoval aktuální git stav (branch, HEAD, čistý worktree) a vrátil historii předchozích sezení.

## ROZHODNUTÍ — VARIANTA (dle RULE 5 SES-000)

| Varianta | Výhody | Nevýhody | Riziko | Doporučení |
|---|---|---|---|---|
| A) Vytvořit nový `.starcore/` na rootu dle doslovné specifikace SPOS-000 §3 | Formální soulad s promptem | Duplicitní, konfliktní systém paměti (dvě pravdy) | VYSOKÉ — fragmentace stavu, matoucí pro budoucí sezení | ❌ NEDOPORUČENO |
| B) Adoptovat `platform/.starcore/` jako kanonickou SPOS implementaci, zdokumentovat mapping | Žádná duplicita, využívá zralý, otestovaný systém | Neodpovídá doslovně SPOS-000 §3 cestě (root vs. `platform/`) | NÍZKÉ | ✅ DOPORUČENO — přijato |

**Zdůvodnění:** `platform/` je jediná vrstva plně v souladu se SES-001 (viz SES-001 §2). Umístění operační paměti uvnitř `platform/` je architektonicky správné — persistentní stav se týká primárně kódu a vývoje platformy, ne celého heterogenního ekosystému root adresářů.

---

## MAPOVÁNÍ SPOS-001..010 NA EXISTUJÍCÍ SYSTÉM

| Modul | Popis (SPOS-000 §2) | Existující implementace | Stav |
|---|---|---|---|
| SPOS-001 | Project Memory | `platform/.starcore/memory/*.md` (9 souborů) | ✅ PLNĚ POKRYTO |
| SPOS-002 | Session Management | `platform/.starcore/sessions/` + `scripts/ledger.py` | ✅ PLNĚ POKRYTO |
| SPOS-003 | Prompt Registry | `platform/.starcore/prompts/registry.yaml` + `scripts/registry.py` | ✅ PLNĚ POKRYTO |
| SPOS-004 | Project Intelligence | `scripts/impact_analyzer.py` (change → module → impact) | ✅ ČÁSTEČNĚ POKRYTO (impact analýza ano, širší "intelligence" ne) |
| SPOS-005 | Audit Engine | `scripts/qc_engine.py`, `regression_sentinel.py`, `release_readiness.py` (12 gates) | ✅ PLNĚ POKRYTO (repo/security/regression audit) |
| SPOS-006 | Documentation Engine | ❌ NEEXISTUJE jako automatizovaný modul | ❌ GAP — mitigováno manuálně přes `.claude/registry/DOCUMENTATION_REGISTRY.md` |
| SPOS-007 | Infrastructure Control | ❌ NEEXISTUJE (žádný Proxmox/Docker control script v `.starcore/`) | ❌ GAP — funkčně pokryto jinde (`platform/packages/providers`), ale ne jako SPOS modul |
| SPOS-008 | AI Orchestration | ❌ NEEXISTUJE jako formální modul | ❌ GAP — Decision Engine (`decision_engine.py`) částečně pokrývá AI rozhodovací formát |
| SPOS-009 | Evolution Engine | ❌ NEEXISTUJE | ❌ GAP — žádný mechanismus pro řízenou evoluci promptů/architektury |
| SPOS-010 | Digital Twin Runtime | `platform/.starcore/memory/project_snapshot.md` (statický) vs. `.claude/context/DIGITAL_TWIN.md` (nový, ekosystémový) | ⚠️ DUPLICITNÍ KONCEPT — viz níže |

---

## DIGITAL TWIN — SJEDNOCENÍ (SPOS-010)

Existují nyní **dva** dokumenty plnící podobnou roli:

1. `platform/.starcore/memory/project_snapshot.md` — scope: pouze `platform/` (metriky testů, coverage, architektura platformy). **STALE** — datováno 2026-08-05, uvádí verzi 0.4.0, zatímco aktuální `pyproject.toml` má 0.6.0.
2. `.claude/context/DIGITAL_TWIN.md` — scope: celý ekosystém STARCORE (root i platform), vytvořeno v tomto bootstrapu, aktuální k 2026-08-06.

**Rozhodnutí:** Neslučovat automaticky (riziko přepsání dat, která spravuje jiný automatizovaný systém). Místo toho:
- `.claude/context/DIGITAL_TWIN.md` zůstává **ekosystémový** master (SES/SAKB/SPOS governance vrstva, root-level)
- `platform/.starcore/memory/project_snapshot.md` zůstává **platform-scoped** operační snapshot (spravovaný vlastním tooling)
- Zaznamenáno jako riziko: `project_snapshot.md` je zastaralý (verze 0.4.0 vs. realita 0.6.0) — **doporučení pro vlastníka projektu:** spustit `uv run python .starcore/scripts/startup_protocol.py` a ručně/skriptem obnovit snapshot při příští pracovní session v tomto systému.

---

## OPRAVA PŘEDCHOZÍHO ZJIŠTĚNÍ (SES-001)

Při ověřování `platform/.starcore/memory/pending_work.md` (položky R-008, R-010 CLOSED) byl odhalen nesoulad s dřívějším SES-001 hodnocením "Dependabot/SBOM chybí". Realita: **existují**, ale jsou umístěny v `platform/.github/` — GitHub však načítá pouze `.github/` v kořeni repozitáře, takže tyto konfigurace jsou **orphaned/neaktivní**. Oprava zanesena přímo do `SES-001-TECHNICAL-STANDARD.md` §5.

---

## PHASE 3-4 — VYTVOŘENÁ STRUKTURA (nedestruktivní, root-level governance vrstva)

Nevytváří se duplicitní `.starcore/`. Místo toho:

```
.claude/
├── spos/
│   └── SPOS-000-RUNTIME-BOOTSTRAP.md   ← tento dokument
└── registry/
    └── SPOS_REGISTRY.md                 ← nový — mapuje SPOS-001..010 stav
```

---

## RIZIKA

| Riziko | Závažnost | Mitigace |
|---|---|---|
| `project_snapshot.md` zastaralý (v0.4.0 vs realita v0.6.0) | STŘEDNÍ | Doporučeno spustit startup_protocol/refresh při příští platform-scoped session |
| Dependabot/SBOM config orphaned v `platform/.github/` | STŘEDNÍ | Zaznamenáno, čeká na schválení přesunu (P010) |
| SPOS-006, 007, 008, 009 nemají formální implementaci | NÍZKÉ | Funkcionalita existuje jinde v projektu (jen ne jako pojmenovaný SPOS modul); dokumentováno jako gap, ne blokující |
| Dva "digital twin" dokumenty s různým scope | NÍZKÉ | Explicitně odděleny a zdokumentovány (ekosystém vs. platform) |

---

## NEXT

Čekat na **SPOS-001 — Project Memory Engine** (mělo by dále rozvíjet/rozšířit existující `platform/.starcore/memory/`, ne ji nahrazovat).
