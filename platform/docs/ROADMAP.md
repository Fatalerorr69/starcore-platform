# STARCORE Platform — Roadmap

## Účel tohoto dokumentu

Vysokoúrovňový, pomalu se měnící přehled směru vývoje STARCORE Platform.
Popisuje *co* je hotové, *co* se právě řeší, a *co* je vize bez závazku
k datu. Pro živý, granulární seznam úkolů viz
`.starcore/memory/pending_work.md` (soubor mimo tento dokumentační strom —
`.starcore/` není publikovaná MkDocs dokumentace) — viz sekce "Hranice"
níže.

Tento dokument se řídí ADR-022 (Documentation Boundary): žije výhradně v
`platform/docs/` a popisuje pouze `platform/` (ADR-018) — nikoli root
legacy vrstvu, která je zmrazena dle ADR-020.

## Aktuální stav

| Metrika | Hodnota |
|---|---|
| Verze | 0.4.0 |
| Testy | 805 collected (current regression baseline), 100% coverage |
| ADR | 25 (ADR-001–017 produktové, ADR-018–025 governance) |
| CI | ruff, pyright, bandit, pip-audit, pytest, alembic check, mkdocs --strict — vše PASS |

## Dokončené milníky

- **v0.1.0–v0.4.0** — Provider SDK, Docker/Proxmox providery, Blueprint
  engine (sekvenční i paralelní), CLI, FastAPI Core API, observabilita
  (Prometheus + structured logging), plugin systém, AI blueprint
  generování, snapshoty, per-task timeouty. Detail: `CHANGELOG.md`,
  `docs/adr/ADR-001` až `ADR-017`.
- **STARCORE Architecture Governance (2026-08-06)** — ADR-018 až ADR-025:
  hranice `platform/` vs. repository root, extension policy, legacy
  freeze, AI layer konsolidace, dokumentační hranice, SAEF jako workflow
  protokol, Android/Termux Edge Node architektura, Change Governance
  Lifecycle. Detail: `docs/adr/ADR-018` až `ADR-025`,
  `.starcore/memory/completed_work.md`.

## Aktivní roadmap položky

Zdroj: `.starcore/memory/pending_work.md` (P2, k dnešnímu dni):

- **Provider concurrency policy — Kubernetes doplnění** (ADR-013): zvážit
  aktualizaci s poznámkou o Kubernetes SDK thread safety po přidání
  třetího provideru. Nízká priorita.
- **docker-compose eager interpolation** — kosmetická vrstva, pravděpodobně
  neřešit vůbec.

## Budoucí fáze (Not Started)

Delší horizont, bez závazku k implementaci. Nic v této sekci dosud
neexistuje jako kód:

| Komponenta | Poznámka |
|---|---|
| Installer Studio | Not started |
| Dashboard (Web UI) | Not started — odlišné od read-only dashboardu na `GET /ui` |
| AI Brain | Not started |
| Marketplace | Not started |
| **STARCORE Edge Node** (Android/Termux) | Not started — architektura rozhodnuta v ADR-024; podrobný implementační design bude doplněn v `docs/architecture/edge-node.md` ve stejné implementační iteraci jako toto ROADMAP.md. Samostatný klient komunikující přes existující API, mimo `platform/` (ADR-018/019). |

Podrobnější dlouhodobá vize: `docs/ses/SES-0000-MASTER-INDEX.md`.

## Hranice mezi ROADMAP.md a pending_work.md

- **`pending_work.md`** je živý, granulární, často aktualizovaný zdroj
  pravdy pro konkrétní úkoly, rizika a jejich prioritu — aktualizuje se
  při každé změně scope.
- **`ROADMAP.md`** je stabilnější, vysokoúrovňový přehled — aktualizuje se
  jen při dokončení milníku nebo přidání nové budoucí fáze, ne při každém
  drobném úkolu.
- Při rozporu mezi oběma dokumenty **`pending_work.md` má přednost** jako
  aktuálnější zdroj.
