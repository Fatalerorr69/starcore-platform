# User Preferences — STARCORE Autonomous Agent

> Pravidla a preference pro komunikaci a chování agenta.
> **Poslední aktualizace:** 2026-07-27

## Jazyk a komunikační styl

- **Primární jazyk:** Česky — všechny reporty, analýzy, volby a komunikace
- **Výjimky:** Technické termíny, názvy souborů, git příkazy, CLI výstupy — vždy v angličtině
- **Styl:** Stručný, technický, bez zbytečného povídání; preference pro strukturované výstupy (tabulky, sekce)
- **Doporučení:** Vždy označit jako `**Doporučení:**` nebo `doporučuji`

## Approval pravidla

### Autonomní akce (bez dotazování)
- Čtení libovolného souboru
- Spouštění testů a linters
- Vytváření nových souborů v `.starcore/`
- Opravy bugů, refactoring — pokud jsou SAFE + REVERSIBLE + WITHIN_SCOPE
- Git add + commit (ne push) na dev větvi

### Vyžaduje explicitní souhlas
- `git push` na jakoukoli větev
- Vytvoření PR
- Smazání souborů (pokud nejsou evidentně stale/temp)
- Force push (NIKDY bez explicitního schválení)
- Rewrite git history
- Modifikace produkční infrastruktury
- Reset dirty workspace bez zálohy

### Zakázáno absolutně
- Commit nebo zobrazení secrets/credentials/API keys
- Force push na `main`
- `git reset --hard` bez zálohy
- Přidání `STARCORE_TASK_TIMEOUT_SECONDS` global timeout (ADR-016 explicitně zamítlo)

## Interaktivní rozhodovací protokol

Při každém nejednoznačném rozhodnutí:
1. Vysvětlit situaci stručně
2. Nabídnout číslované možnosti s jasným popisem
3. Označit doporučenou možnost jako `(doporučeno)`
4. Zakončit frází `ČEKÁM NA VOLBU`

## Commit konvence

- Conventional Commits: `fix:`, `feat:`, `docs:`, `ci:`, `refactor:`, `test:`
- Scope v závorkách kde relevantní: `fix(timeout):`, `ci:`, `docs(adr):`
- Zprávy v angličtině
- Stručné, výstižné

## Reportovací šablona (na konci implementačních sezení)

```
STAV: <OK|WARNING|ERROR>

IMPLEMENTOVANÉ: <seznam>
OVĚŘENÉ: <seznam>
TESTY: <počet passed, % coverage>
NOVÉ SOUBORY: <seznam>
ZMĚNĚNÉ SOUBORY: <seznam>
RIZIKA: <seznam aktivních rizik>
ROLLBACK: <instrukce>
DOPORUČENÍ: <doporučení pro příští sezení>

ACTION_REQUIRED:
[1] <možnost>
[2] <možnost>
[3] <možnost>
[4] Jiná instrukce
WAITING_FOR_USER_CHOICE
```

## Phase-gated protokol

Sezení jsou organizována do fází (Phase 1, 2, ... 9). Každá fáze:
1. Začíná explicitním promptem od uživatele
2. Končí PHASE_COMPLETE / CURRENT_PHASE=X / NEXT_PHASE=Y / WAITING_FOR_NEXT_PROMPT_PART
3. Agent NESMÍ přejít do další fáze bez výzvy

## Dev větev

Veškerá práce jde na: `claude/starcore-autonomous-engineering-4p3tlj`
Nikdy push na `main` bez explicitního pokynu.
