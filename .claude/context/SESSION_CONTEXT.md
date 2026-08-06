# SESSION CONTEXT — STARCORE

Standard: SPOS-002 §6 | Aktualizováno: 2026-08-06

> Generováno na začátku/v průběhu session dle SPOS-002 §5-6. Strojově čitelný zdroj:
> `platform/.starcore/sessions/ledger.yaml` (aktivní záznam), doplněk k `.claude/context/DIGITAL_TWIN.md`.

---

## PROJECT STATUS

STARCORE Platform v0.6.0 — probíhá SES/SAKB/SPOS governance bootstrap (viz `.claude/ses/SES-INDEX.md`).

## CURRENT OBJECTIVE

Postupná implementace governance frameworku: SES-000 → SES-001 → SAKB-000 → SPOS-000 → SPOS-001 → **SPOS-002 (aktuální)** → SPOS-003+ (očekává se).

## PREVIOUS WORK

| Krok | Výsledek |
|---|---|
| Bootstrap 00 | Discovery reports, `.claude/` struktura |
| SES-000 | Engineering Constitution registrována |
| SES-001 | Technical Standard, gap analýza (Dependabot/SBOM orphaned finding) |
| SAKB-000 | Knowledge Base struktura, 6 Technology Profiles |
| SPOS-000 | Adopce existujícího `platform/.starcore/` runtime (neduplikováno) |
| SPOS-001 | Rozšíření memory o `current_state.md` + `project_state.json` |

## CURRENT TASK

SPOS-002 — Session Management Engine:
- Audit `platform/.starcore/sessions/` (ledger.yaml, current.md, archive/)
- Nalezena a uzavřena osiřelá session (`starcore-autonomous-engineering-4p3tlj`, end_time byl null)
- Zaregistrována aktuální bootstrap session (`claude/starcore-ai-bootstrap-fkyb96`) v ledgeru
- Ověřeno: `_archive_session()` v `ledger.py` již plně pokrývá §8 Handover Report formát

## DEPENDENCIES

- `platform/.starcore/scripts/ledger.py` (nezměněn, jen použit)
- `.claude/context/CONTEXT_RESTORATION_PROTOCOL.md` (SPOS-001, předpoklad pro cold-start)

## KNOWN RISKS

Viz `platform/.starcore/state/project_state.json` → `risks` (živý zdroj) a ledger `add-risk` záznamy této session.

## NEXT STEPS

Čekat na **SPOS-003 — Prompt Registry Engine**.
