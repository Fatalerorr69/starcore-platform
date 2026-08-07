# DUPLICATE REGISTRY

Standard: SPOS-015 §6 | Aktualizováno: 2026-08-07

Registr duplicitní logiky identifikované v platform/ kódu.

---

## IDENTIFIKOVANÉ DUPLIKACE

### DUP-001 — _persist_run() copy-paste

```yaml
id: DUP-001
severity: MEDIUM
type: EXACT_COPY
files:
  - "platform/packages/core/routers/blueprints.py:177"
  - "platform/packages/core/routers/ws.py:202"
lines: 6
description: "Identická 6-řádková funkce _persist_run() zkopírovaná mezi dvěma routery."
recommendation: "Extrahovat do packages/core/persistence.py nebo sdíleného modulu."
effort: XS
```

### DUP-002 — Provider connection-failure boilerplate

```yaml
id: DUP-002
severity: LOW
type: STRUCTURAL_PATTERN
files:
  - "platform/packages/providers/docker/provider.py"
  - "platform/packages/providers/proxmox/provider.py"
  - "platform/packages/providers/kubernetes/provider.py"
lines: "~10 × 3"
description: "Všichni tři provideři opakují identický pattern: import scrub_configured_secrets, try connection, logger.error s scrub, set client=None, return False."
recommendation: "Přijatelné — ABC pattern vyžaduje opakování v subclassech. Případně template method v BaseProvider."
effort: S
```

### DUP-003 — get_settings() repeated instantiation

```yaml
id: DUP-003
severity: LOW
type: ANTIPATTERN
files:
  - "platform/packages/core/diagnostics.py (4× volání)"
  - "10+ dalších souborů"
description: "get_settings() je voláno opakovaně v rámci jedné funkce místo uložení do lokální proměnné. POZNÁMKA: get_settings() JE cachováno přes @lru_cache, takže opakovaná volání NEVYTVÁŘÍ nové instance — je to pouze stylistický problém, ne výkonnostní."
recommendation: "Stylisticky preferovat jednu lokální proměnnou per scope. Funkčně bezproblémové."
effort: XS
```

---

## STATISTIKY

```yaml
total_duplicates: 3
exact_copies: 1 (DUP-001)
structural_patterns: 1 (DUP-002)
antipatterns: 1 (DUP-003)
severity_medium: 1
severity_low: 2
```
