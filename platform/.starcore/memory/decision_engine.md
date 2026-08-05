# STARCORE Interactive Decision Engine — Protokol

## Účel

Decision Engine definuje standardní formát pro každou smysluplnou interakci
(po auditu, implementaci, selhání) mezi STARCORE agentem a uživatelem.

Zajišťuje:
- konzistentní strukturu reportů (8 pevných sekcí)
- explicitní volby [1]–[N] namísto implicitního pokračování
- bezpečnostní brány pro destruktivní operace
- integraci se session ledgerem

---

## Standardní formát reportu

```
────────────────────────────────────────────────────────────────────────
## STAV
OK | CHYBA | VAROVÁNÍ | BLOKOVÁNO

## CO BYLO ZJIŠTĚNO
- Zjištění 1
- Zjištění 2

## CO BYLO OVĚŘENO
- Ověřeno 1
- Ověřeno 2

## RIZIKA
- R-XXX: popis [HIGH/MED/LOW]

## DOPORUČENÍ

### Doporučená varianta
[1] Popis doporučené akce

### Alternativy
[2] Alternativa A
[3] Alternativa B
[4] Pokračovat v auditu
[5] Zobrazit detail
[6] Vlastní instrukce

## DOPAD
Popis dopadu doporučené varianty

## RIZIKO
LOW | MEDIUM | HIGH

## ROLLBACK
git revert HEAD / git checkout -- <soubor>

## DALŠÍ KROK
Čekám na volbu [1]–[6].
────────────────────────────────────────────────────────────────────────
Čekám na tvoji volbu.
```

---

## Kdy použít Decision Engine formát

Povinně po každé z těchto událostí:

| Událost | Sekce povinné |
|---------|---------------|
| Audit / statická analýza | všechny |
| Implementace (commit/push) | STAV, OVĚŘENO, RIZIKA, DOPORUČENÍ, ROLLBACK |
| Selhání CI / testu | CO BYLO ZJIŠTĚNO, RIZIKA, DOPORUČENÍ |
| Detekce nového rizika | RIZIKA, DOPORUČENÍ, DOPAD |
| Konec sezení | STAV, OVĚŘENO, DOPORUČENÍ |

---

## Parsování volby uživatele

Decision Engine rozumí těmto formátům:

| Vstup uživatele | Výsledek |
|-----------------|----------|
| `1` | choice=1 |
| `Varianta 1` | choice=1 |
| `Vyber 2` | choice=2 |
| `[3]` | choice=3 |
| `Pokračuj` | choice=1 (doporučená) |
| `Pokračovat` | choice=1 |
| `Proveď doporučenou variantu` | choice=1 |
| `audit` | choice=4 |
| `detail` | choice=5 |
| `vlastní instrukce` | choice=6 |
| `Oprav R-001` | semantic: "oprav r-001" |
| `Zobraz R-010` | semantic: "zobraz r-010" |
| `Implementuj variantu` | semantic: "implementuj variantu" |

---

## Bezpečnostní brány

Tyto operace vyžadují explicitní potvrzení uživatelem (nikdy autonomní):

- `merge`, `push`, `delete`, `drop`, `remove`, `reset`
- `--force`, `-f`
- `force push`, `git push --force`, `git reset --hard`, `git clean`
- `infrastructure`, `production`, `prod`
- `secret`, `credential`, `password`, `token`, `api key`
- `rm -rf`, `truncate`, `drop table`

Bezpečné reverzibilní operace (autonomní provádění povoleno):
- čtení souborů, grep, git status, git log
- pytest, ruff check, pyright
- vytváření nových souborů (ne přepisování)

---

## CLI nástroje

```bash
# Vykreslit report ze YAML souboru
uv run python .starcore/scripts/decision_engine.py render --file report.yaml

# Vykreslit report ze stdin
cat report.yaml | uv run python .starcore/scripts/decision_engine.py render --file -

# Parsovat volbu uživatele
uv run python .starcore/scripts/decision_engine.py parse-choice "Varianta 2"
# → choice=2

# Ověřit bezpečnost operace
uv run python .starcore/scripts/decision_engine.py check-safety "git push --force"
# exit 0 = SAFE, exit 2 = REQUIRES_CONFIRMATION

# Zobrazit prázdnou šablonu
uv run python .starcore/scripts/decision_engine.py format

# Zalogovat rozhodnutí do session ledgeru
uv run python .starcore/scripts/decision_engine.py log --decision "Zvolena varianta 1: SHA pinning"
```

---

## Integrace se session ledgerem

Každé rozhodnutí zvolené uživatelem se automaticky loguje:

```bash
uv run python .starcore/scripts/decision_engine.py log \
  --decision "Uživatel zvolil [1]: implementovat SHA pinning (R-001)"
```

Tím se volba zapíše do `sessions/ledger.yaml` → `decisions[]` pro aktuální sezení.

---

## YAML schéma reportu

```yaml
stav: "OK | CHYBA | VAROVÁNÍ"
zjisteno:
  - "Zjištění 1"          # nebo string
  - "Zjištění 2"
overeno:
  - "Ověřeno 1"
rizika:
  - "R-XXX: popis [HIGH/MED/LOW]"
doporuceni: "Text doporučené akce"
alternativy:
  - "Alternativa A"
  - "Alternativa B"
dopad: "Popis dopadu"
riziko_uroven: "LOW | MEDIUM | HIGH"
rollback: "git revert HEAD"
dalsi_krok: "Čekám na volbu [1]–[6]."
standard_choices: true   # false = nepřidávat [4]/[5]/[6]
```

---

## Testy

```bash
uv run python .starcore/scripts/tests/test_decision_engine.py
# → 49/49 testů prošlo
```

Testy pokrývají:
- `parse_choice`: 22 vstupních formátů
- `requires_confirmation`: 5 safe + 10 unsafe operací
- `render_report`: 12 assertions (sekce, volby, formátování)
