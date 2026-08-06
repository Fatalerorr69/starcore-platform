# PROMPT REGISTRY

Standard: SPOS-003 §19 | Aktualizováno: 2026-08-06

Ekosystémový index promptů. Strojově čitelný zdroj pravdy: `platform/.starcore/prompts/registry.yaml` (spravováno přes `registry.py` CLI — viz SPOS_REGISTRY.md → Automation CLI).

---

## GOVERNANCE PROMPTY (tato bootstrap session)

| ID | Název | Typ | Status | Závislosti |
|---|---|---|---|---|
| SES-000 | STARCORE Engineering Constitution | MASTER | ✅ ACTIVE | — |
| SES-001 | STARCORE Technical Engineering Standard | MASTER | ✅ ACTIVE | SES-000 |
| SAKB-000 | STARCORE AI Knowledge Base Model | MASTER | ✅ ACTIVE | SES-000, SES-001 |
| SPOS-000 | Runtime Bootstrap | MASTER | ✅ ACTIVE | SES-000, SES-001, SAKB-000 |
| SPOS-001 | Project Memory Engine | IMPLEMENTATION | ✅ ACTIVE | SPOS-000 |
| SPOS-002 | Session Management Engine | IMPLEMENTATION | ✅ ACTIVE | SPOS-001 |
| SPOS-003 | Prompt Registry Engine | IMPLEMENTATION | ✅ ACTIVE | SPOS-000, SPOS-001, SPOS-002 |

## HISTORICKÉ PROMPTY (předchozí session, `starcore-autonomous-engineering-4p3tlj`)

| ID | Název | Typ | Status |
|---|---|---|---|
| PROM-001 | STARCORE MASTER AUTONOMOUS ENGINEERING SESSION | MASTER | ACTIVE |
| PROM-002 | STARCORE WORKSPACE ENHANCEMENT BOOTSTRAP v1.0 | AUDIT | ACTIVE |
| PROM-003 | STARCORE WORKSPACE MEMORY IMPLEMENTATION v1.0 | IMPLEMENTATION | ACTIVE |
| PROM-004 | STARCORE FINAL OPERATING MODE | MASTER | ACTIVE |
| PROM-005 | STARCORE PHASE 8 — CONTROLLED IMPLEMENTATION | IMPLEMENTATION | ARCHIVED |
| PROM-006 | STARCORE PROMPT REGISTRY AND SESSION LEDGER v1.0 | IMPLEMENTATION | ACTIVE |
| PROM-007 | STARCORE MASTER AUTONOMOUS ENGINEERING SESSION v2.0 | MASTER | REJECTED |
| PROM-008 | Test Prompt pro Validaci | UTILITY | REJECTED |

---

## STATISTIKY

```yaml
total_prompts: 15
active: 12
archived: 1
rejected: 2
latest_executed: SPOS-003
```

---

## DEPENDENCY GRAPH (governance prompty)

```
SES-000
  └─ SES-001
       └─ SAKB-000
            └─ SPOS-000
                 └─ SPOS-001
                      └─ SPOS-002
                           └─ SPOS-003 (nejnovější)
```

---

## ZNÁMÉ MEZERY (SPOS-003 §5 vs realita)

`PromptEntry` model (`platform/.starcore/scripts/models.py`) nemá explicitní pole `RELATED_FILES`, `RELATED_COMMITS`, `VALIDATION_STATUS`, `INPUTS`, `OUTPUTS` ze spec §5. Tyto informace jsou dostupné nepřímo:
- RELATED_FILES / RELATED_COMMITS → přes session ledger (`files_created`/`files_modified` v aktivní/archivované session, propojené `add-prompt`)
- VALIDATION_STATUS → přes `registry.py validate` (globální, ne per-prompt)
- INPUTS/OUTPUTS → v `description` poli (nestrukturovaně)

**Rozhodnutí:** Nerozšiřovat `PromptEntry` dataclass (riziko zásahu do otestovaného kódu, 384 řádků `registry.py` + testy) — zaznamenáno jako vědomá mezera, ne blokující.

§16 GitHub integrace ("Implemented by: PROM-XXX" v commit zprávách) — doporučeno pro budoucí commity, historické commity nepřepisovány (destruktivní operace, mimo scope).
