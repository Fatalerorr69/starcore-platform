# SESSION REGISTRY

Standard: SPOS-002 §18 | Aktualizováno: 2026-08-06

Index sessions napříč ekosystémem. Strojově čitelný zdroj pravdy: `platform/.starcore/sessions/ledger.yaml`. Tento registr je jeho lehký ekosystémový index (root-level, pro `.claude/` governance vrstvu).

---

| Session ID | Start | End | Branch | Status | Archiv |
|---|---|---|---|---|---|
| starcore-autonomous-engineering-4p3tlj | 2026-07-26 | 2026-08-06 (retroaktivně) | claude/starcore-autonomous-engineering-4p3tlj | ✅ UZAVŘENO | `platform/.starcore/sessions/archive/2026-07-26-starcore-autonomous-engineering-4p3tlj.md` |
| claude/starcore-ai-bootstrap-fkyb96 | 2026-08-06 | — | claude/starcore-ai-bootstrap-fkyb96 | 🟢 AKTIVNÍ | — (probíhá) |

---

## AUDIT FINDING (SPOS-002 discovery)

Session `starcore-autonomous-engineering-4p3tlj` měla `end_time: null` od 2026-07-26 do objevení při SPOS-002 auditu (2026-08-06) — nikdy nebyla formálně uzavřena předchozím agentem/uživatelem. Retroaktivně uzavřena přes `ledger.py end` s poznámkou vysvětlující kontext. Žádná data nebyla vymyšlena — `next_action` pole odkazuje na `completed_work.md` jako zdroj skutečných výsledků.

## NÁSTROJE

Správa přes `platform/.starcore/scripts/ledger.py` (viz `.claude/registry/SPOS_REGISTRY.md` → Automation CLI).

```bash
cd platform && python3 .starcore/scripts/ledger.py list
cd platform && python3 .starcore/scripts/ledger.py current
cd platform && python3 .starcore/scripts/ledger.py validate
```
