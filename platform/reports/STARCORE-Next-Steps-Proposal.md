# STARCORE Platform — Odborný návrh dalšího rozvoje

**Autor:** Claude Code (senior reviewer / stabilizační inženýr)
**Datum:** 2026-07-26
**Navazuje na:** `STARCORE-Platform-Audit-Report-2026-07-26.md`
**Účel:** Konkrétní, prioritizovaný návrh dalších kroků nad rámec toho, co bylo v tomto sprintu opraveno. Toto je doporučení, ne provedená práce — nic z tohoto dokumentu nebylo implementováno bez výslovného zadání.

---

## Jak číst tento dokument

Doporučení jsou seřazená podle poměru **dopad / námaha**, ne podle abstraktní důležitosti. U každého bodu je uvedeno: proč to navrhuji (konkrétní důkaz z repozitáře, ne dojem), co by to stálo, a co by to chránilo. Priority:

- **P0** — udělal bych dřív, než přibude další funkcionalita.
- **P1** — udělal bych v příštích 1–2 sprintech.
- **P2** — hodnotné, ale bezpečně odložitelné.
- **Nápad k diskuzi** — netriviální architektonické rozhodnutí, které by mělo padnout vědomě, ne jako vedlejší efekt jiné práce.

---

## P0 — Rozhodnout o sémantice selhání závislostí (RISK-05)

Toto je jediná věc z tohoto auditu, kterou bych řešil první, protože je to
**tichá nejednoznačnost v jádru hodnoty produktu** — orchestraci
infrastruktury. Dnes: pokud resource `A` selže a resource `B` na něm závisí
(`depends_on: [A]`), `B` se **přesto pokusí provést**, protože `depends_on`
funguje jen jako řazení, ne jako brána úspěchu (ověřeno přímo v kódu
`scheduler.py` i `executor.py`, viz audit report §3.2).

To může být v pořádku pro homelab nástroj ("best effort, nahlas všechny
chyby najednou"), ale pro nástroj, který vytváří skutečnou infrastrukturu
(VM, kontejnery, storage), je tichá kontinuace po selhání prerekvizity
rizikové chování — může vzniknout VM napojená na síť, která se nikdy
nevytvořila.

**Návrh řešení (2 varianty, obě proveditelné v rozsahu jednoho sprintu):**

1. **Minimální varianta** — nový stav `TaskStatus.SKIPPED_DEPENDENCY_FAILED`.
   V obou execution paths (`Scheduler._run_task`, `BlueprintExecutor.execute`)
   před spuštěním úlohy zkontrolovat, zda všechny `depends_on` úlohy mají
   `status == SUCCESS`; pokud ne, nastavit nový status a nevolat
   `provider.execute()`. Malá, izolovaná změna — cca 10 řádků na path,
   testy už existují jako základ (regresní testy z tohoto sprintu se dají
   přepsat na nové očekávané chování).
2. **Konfigurovatelná varianta** — přidat do `Blueprint` nepovinné pole
   `on_dependency_failure: "skip" | "continue"` (default `"continue"` = dnešní
   chování, zpětně kompatibilní), aby uživatel mohl zvolit podle use-case.
   Víc práce (schema, dokumentace, CLI plan output), ale nerozbije nikoho.

Doporučuji začít **variantou 1** jako ADR-009, protože je to jasnější a
menší závazek. Pokud se ukáže, že uživatelé chtějí "continue" chování,
lze přidat konfigurovatelnost později — to je levnější směr změny než
opačný.

---

## P0 — Doplnit „secrets in response body" kontrolu do code review checklistu

Nález RISK-NEW-2 (únik `DATABASE_URL` přes `/health`) prošel 100% pokrytím
testy, čistým Banditem i gitleaks skenem — protože žádný z těchto nástrojů
nekontroluje, **co konkrétní endpoint vrací**, jen jestli je něco spuštěno a
jestli literál v kódu vypadá jako tajemství. To je systémová mezera, ne
náhoda.

**Návrh:** Přidat do `CONTRIBUTING.md` (nebo do PR šablony) jednu
kontrolní otázku, vyžadovanou u každého PR, který přidává/mění pole v
response nějakého endpointu nebo `--json` výstupu CLI: *"Může toto pole
obsahovat cokoliv, co by neautentizovaný volající neměl vidět?"* Nulové
náklady na implementaci, vysoká návratnost — přesně tento typ nálezu se
nedá odchytit nástrojem, jen návykem.

---

## P1 — Rozšířit Bandit/gitleaks o sanitizaci response bodies (test úroveň)

Nad rámec P0 výše bych zvážil jeden malý, ale trvalý test: `test_health.py`
nebo `test_api.py` by měl obsahovat parametrizovaný test, který nastaví
`STARCORE_DATABASE_URL` na DSN s embedded credentials a ověří, že **žádný**
endpoint dostupný bez `X-API-Key` (tj. `/`, `/health`, `/ui`) neobsahuje ve své
odpovědi substring hesla. Tohle by bylo obecnější než regresní test přidaný
v tomto sprintu (který testuje jen `check_database_connectivity()` přímo) —
chránilo by to i budoucí endpointy, které by omylem znovu použily
`settings.database_url` bez redakce.

Odhad práce: ~30 minut, jeden nový test soubor nebo rozšíření
`test_health.py`.

---

## P1 — ADR pro RISK-06 (plugin trust boundary) a RISK-07 (mrtvý flag)

Obě jsou levné (jeden odstavec dokumentace, případně jeden `if`), ale mají
smysl udělat společně s P0 bodem výš, protože jde o stejnou kategorii práce
("dokumentovat/rozhodnout, co dnes kód dělá implicitně"). Konkrétně:

- `docs/architecture.md`, sekce Plugin System: jedna věta o tom, že
  `plugins/` adresář musí být stejně důvěryhodný jako proces samotný
  (import spouští kód okamžitě).
- `apps/cli/main.py`: buď `--non-interactive` skutečně zapojit (potlačit
  Rich prompty, force `--yes` chování u destructive příkazů jako
  `snapshot delete`/`rollback`), nebo flag odstranit, aby nepůsobil dojmem
  funkčnosti, kterou nemá.

---

## P2 — Observabilita: request-scoped correlation ID

`packages/core/logger.py` už má structured/JSON logging (`STARCORE_LOG_JSON`),
což je dobrý základ. Chybí ale request-scoped correlation ID prostupující
FastAPI middleware → business logiku → provider volání → log řádky. Bez
něj je v produkčním nasazení těžké spárovat "tenhle HTTP request" s "těmito
třemi log řádky o Proxmox API volání o 200ms později", zvlášť pod
paralelním schedulerem, kde běží víc úloh najednou.

**Návrh:** Middleware, který vygeneruje/přečte `X-Request-ID`, uloží ho do
`contextvars.ContextVar`, a `core/logger.py`'s Loguru konfigurace ho
automaticky připojí ke každému řádku. Malý, izolovaný, nemění žádné
existující chování — čistě přídavek k observabilitě. Odhad: půl dne včetně
testů.

---

## P2 — Snapshot/rollback bezpečnostní pojistka: dry-run diff

`starcore snapshot rollback` už vyžaduje potvrzení (`--yes` flag). Šel bych
o krok dál: před samotným rollbackem vypsat, co přesně se změní (aktuální
stav VM/LXC vs. stav ve snapshotu — hlavně running/stopped status a
přidělené resources), podobně jako `blueprint plan` ukazuje plán před `run`.
Toto by odpovídalo existujícímu vzoru "vždy ukázat plán před destructive
akcí", který je v CLI jinde dobře dodržený (`blueprint plan` vs.
`blueprint run`).

---

## P2 — Sjednotit "Co je hotovo" dokumentaci

`README.md` má sekci nadepsanou **"What's Planned, Not Built Yet"**, ale
všechny řádky pod ní mají status `Done`. To je matoucí pro nového
přispěvatele (nebo mě v příštím auditu) — vypadá to jako pozůstatek staré
struktury dokumentu z doby, kdy tam skutečně bylo něco neimplementovaného.
Navrhuji buď přejmenovat sekci na něco jako "Recently Completed" nebo ji
sloučit s tabulkou výš ("What Works Today"), pokud už žádná skutečně
neimplementovaná položka neexistuje. Čistě kosmetické, ale dokumentační
drift má tendenci se hromadit, pokud se neřeší průběžně.

---

## Nápad k diskuzi — Multi-provider paralelismus v rámci jedné vlny

`Scheduler.execute()` dnes spouští všechny úlohy jedné vlny přes
`asyncio.gather`, což je správné pro I/O-bound provider volání. Až přibudou
další provideři (podle `CLAUDE.md` je architektura pro to připravená —
`ProviderRegistry` je obecná), stojí za zvážení: má scheduler nějaký limit
souběžnosti na jednoho providera (např. Proxmox API rate limit), nebo se
spolehá čistě na to, že `_connect_lock` sekvencuje jen `connect()`, ne
`execute()`? Dnes s jedním nebo dvěma providery to není problém, ale je to
otázka, kterou má smysl mít zodpovězenou dřív, než bude ve hře pět
providerů najednou a desítky resources ve vlně. Nejde o nález, jde o
otázku k budoucímu ADR, až (a pokud) nastane potřeba.

---

## Co bych naopak NEdělal

Ve shodě s Master Promptem (sekce 11) a s tím, co audit skutečně ukázal:

- **Neměnil bych execution model** (sequential vs. parallel) — oba jsou
  korektní a slouží různým use-case (CLI default vs. `--parallel`).
  Sjednocení by přidalo komplexitu bez ověřeného přínosu.
- **Nepřidával bych DI framework** — současné module-level singletony jsou
  pro rozsah projektu odpovídající a dobře otestované; DI framework by byl
  řešení problému, který dnes neexistuje.
- **Neintrodukoval bych mikroservisy** ani frontend framework pro `/ui` —
  statický HTML/JS dashboard dělá přesně to, co má, a přidání buildstepu
  (React/Vue) by byl čistý technický dluh bez odpovídající potřeby.
- **Neškáloval bych coverage gate nad 100 %** (např. mutation testing jako
  povinná brána) — hodnotný nápad obecně, ale u projektu této velikosti by
  náklady na údržbu pravděpodobně převýšily přínos v tomto bodě vývoje.
  Zmiňuji jako P2/nápad, ne jako doporučení k okamžité akci.

---

## Souhrn priorit pro příští sprint

| Priorita | Položka | Odhad práce |
|---|---|---|
| P0 | Rozhodnout a implementovat RISK-05 (dependency-failure gate nebo ADR dokumentující "continue" jako záměr) | 0,5–1 den |
| P0 | Přidat "secrets in response" otázku do PR checklistu / CONTRIBUTING.md | 15 minut |
| P1 | Obecný test: žádný neautentizovaný endpoint neobsahuje credentials | 30 minut |
| P1 | ADR/dokumentace pro plugin trust boundary (RISK-06) | 15 minut |
| P1 | Zapojit nebo odstranit `--non-interactive` (RISK-07) | 1–2 hodiny |
| P2 | Request-correlation ID v logování | 0,5 dne |
| P2 | Dry-run diff před `snapshot rollback` | 0,5 dne |
| P2 | Sjednotit "Planned, Not Built Yet" sekci v README | 15 minut |

Toto pořadí odpovídá metodice Master Promptu (§13): determinismus a
bezpečnost první, pak testovatelnost a čitelnost, teprve pak rozšiřování.
