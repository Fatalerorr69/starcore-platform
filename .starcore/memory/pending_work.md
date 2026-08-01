# Pending Work — STARCORE Platform

> Zbývající práce seřazená podle priority. Aktualizovat při každé změně scope.
> **Poslední aktualizace:** 2026-07-27 (po Phase 10 — Startup Protocol)

---

## P1 — Vyřešit brzy

### ~~R-001: GitHub Actions SHA pinning~~ — CLOSED 2026-07-27
- 22 referencí pinned ve všech 7 workflow souborech (commit `c0d2b38`)

### P2 — Deferrable

### ~~R-007: Smazat nebo zakázat jekyll-gh-pages.yml~~ — CLOSED 2026-08-01
- Soubor smazán

### ~~R-008: Omezit Dependabot auto-merge scope~~ — CLOSED 2026-08-01
- Omezeno na `pip` ekosystém; Actions updates vyžadují manuální review

### ~~R-010: SBOM/provenance attestations~~ — CLOSED 2026-08-01
- `cosign sign` + `cosign attest` + `anchore/sbom-action` v `docker-publish.yml`

### ~~R-012: assert guards → if/raise~~ — CLOSED 2026-07-27
- 11 assert statementů → if/raise, 11 testů přidáno (commit viz ledger)

### ~~R-016: Dokumentovat STARCORE_POSTGRES_PASSWORD~~ — CLOSED 2026-07-27
- Přidán řádek do CLAUDE.md config tabulky (docker-compose only)

### ~~R-018: Packaging completeness~~ — CLOSED 2026-07-27
- plugins → packages, migrations + alembic.ini → force-include (wheel 58→65 entries)

---

## P2 — From STARCORE-Next-Steps-Proposal.md (Deferred P2 items)

Tyto položky byly navrženy v předchozím auditu a záměrně odloženy na P2:

### ~~1. Request-scoped correlation ID logging rozšíření~~ — CLOSED (2026-08-01)
- Ověřeno: loguru `contextualize()` prostupuje přes `await` i `asyncio.to_thread()` (Python contextvars)
- Přidány 2 testy: `test_loguru_context_propagates_through_asyncio_to_thread` + `test_request_id_propagates_to_provider_execute_log`
- 582 testů, 100% coverage (commit `1e9c6c5`)

### ~~2. Snapshot rollback dry-run diff~~ — CLOSED (v0.2.0)
- `_show_rollback_preview()` + `_snapshot_rollback_preview()` implementovány a otestovány (11 testů).
  `--yes` přeskočí preview. CHANGELOG [0.2.0] → Added.

### 3. Provider concurrency policy ADR dokument
- **Stav:** ADR-013 existuje (no semaphore; trigger conditions defined)
- **Co zbývá:** Nic urgentního — revisit při přidání třetího providera

### 4. README "What's Planned, Not Built Yet" sekce
- **Stav:** Každý řádek má status `Done` — sekce zavádí
- **Oprava:** Přejmenovat nebo sloučit s "What Works Today"
- **Odhad:** 15 minut

### 5. docker compose config eager interpolation wrinkle
- **Závažnost:** COSMETIC; neovlivňuje real usage
- **Odhad:** Možná neřešit vůbec

---

## Dlouhodobé / architektonické

### Multi-provider rate limiting
- ADR-013 zaznamenalo potenciální potřebu per-provider semaphore pro Proxmox API rate limits
- **Trigger:** Přidání třetího BaseProvider implementace nebo pozorovaný throttling v produkci

### Per-task timeouts (ADR-016)
- `execute_with_timeout()` existuje a je otestováno
- **Trigger:** Blueprint schema získá `timeout_seconds` field; nebo hung task incident v produkci

---

## Poznámka k pořadí

Doporučené pořadí pro příští sezení:
1. **R-001 (SHA pinning)** — nejvyšší bezpečnostní dopad, jasně vymezená práce
2. **R-012 (assert guards)** — rychlá win, zlepšení robustnosti
3. **README cleanup** — 15 minut
4. Pak R-010, R-016, R-018 dle preferencí

Ale **vždy** nejdřív: ověřit git stav, spustit testy, zkontrolovat `sessions/current.md`.
