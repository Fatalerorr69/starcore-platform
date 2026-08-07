# ECOSYSTEM GAP ANALYSIS

Standard: SPOS-015 §9 | Aktualizováno: 2026-08-07

Gap analýza celého STARCORE ekosystému — mezery mezi aktuálním a požadovaným stavem governance.

---

## SUMMARY

```yaml
total_gaps: 15
critical: 3
high: 5
medium: 4
low: 3
```

---

## KRITICKÉ GAPY

### GAP-ECO-001 — 18 legacy adresářů bez governance

```yaml
id: GAP-ECO-001
severity: CRITICAL
category: GOVERNANCE
description: "18 root-level legacy adresářů (core/, control_center/, mission_engine/, studio/, sdk/, hardening/, cli/, config/, bin/, plugins/, sessions/, prompts/, backups/, installers/, templates/, security/, intelligence/, automation/) nemá žádnou formální governance dokumentaci."
impact: "Nové sessions/agenti nemohou rozlišit živý kód od legacy, riskují práci s mrtvým kódem."
recommendation: "Archivovat do legacy/ subdir s README nebo přidat per-directory LEGACY.md"
effort: M
```

### GAP-ECO-002 — Dead code v repozitáři

```yaml
id: GAP-ECO-002
severity: CRITICAL
category: HYGIENE
description: "4 adresáře (github_intelligence/, knowledge_engine/, performance/, api_gateway/) obsahují Python soubory s nulovými referencemi odkudkoli v repozitáři."
impact: "Zvyšuje kognitivní zátěž, zvětšuje git clone, mate nové přispěvatele."
recommendation: "Smazat nebo přesunout do archive/"
effort: XS
```

### GAP-ECO-003 — Prázdné root-level registry

```yaml
id: GAP-ECO-003
severity: CRITICAL
category: HYGIENE
description: "registry/modules.json, registry/sdk_registry.json, runtime/marketplace/registry.json obsahují prázdné seznamy. Nikdy nebyly populovány."
impact: "False impression of module/plugin infrastructure that doesn't exist."
recommendation: "Smazat nebo přesunout do archive/"
effort: XS
```

---

## VYSOKÉ GAPY

### GAP-ECO-004 — Žádný ECOSYSTEM_README

```yaml
id: GAP-ECO-004
severity: HIGH
description: "Root README.md dokumentuje pouze platform/, agents/, runtime/, knowledge/, ale ignoruje 20+ dalších adresářů."
recommendation: "Aktualizovat README.md s kompletní mapou nebo odkázat na ECOSYSTEM_MAP.md"
effort: S
```

### GAP-ECO-005 — platform/.github/ orphaned workflows

```yaml
id: GAP-ECO-005
severity: HIGH
description: "7 workflow souborů v platform/.github/ — GitHub je nikdy nečte (čte pouze root .github/). Identifikováno SPOS-007, stále neopraveno."
recommendation: "Přesunout do root .github/ nebo smazat"
effort: S
```

### GAP-ECO-006 — Broken Termux symlink

```yaml
id: GAP-ECO-006
severity: HIGH
description: "bin/control-center je symlink na /data/data/com.termux/files/home/STARCORE/control_center/bin/control-center — vždy broken mimo Termux."
recommendation: "Smazat nebo archivovat"
effort: XS
```

### GAP-ECO-007 — platform/reports/ orphaned

```yaml
id: GAP-ECO-007
severity: HIGH
description: "12 markdown/JSON reportů v platform/reports/ bez jakékoli governance reference."
recommendation: "Katalogizovat nebo archivovat"
effort: S
```

### GAP-ECO-008 — platform/scripts/ částečně nedokumentované

```yaml
id: GAP-ECO-008
severity: HIGH
description: "3 z 7 souborů v platform/scripts/ (make-executable.sh, quickstart.sh, release.py) nemají žádnou dokumentaci."
recommendation: "Dokumentovat v existujícím registru nebo přidat do DEPLOYMENT_REGISTRY"
effort: XS
```

---

## STŘEDNÍ GAPY

### GAP-ECO-009 — _persist_run() duplicita

```yaml
id: GAP-ECO-009
severity: MEDIUM
description: "Identická 6-řádková funkce _persist_run() v blueprints.py a ws.py."
recommendation: "Extrahovat do sdíleného modulu"
effort: XS
```

### GAP-ECO-010 — Chybějící ADR pro WebSocket streaming

```yaml
id: GAP-ECO-010
severity: MEDIUM
description: "WebSocket blueprint execution (routers/ws.py) nemá ADR dokumentující design decision."
recommendation: "Vytvořit ADR-018"
effort: S
```

### GAP-ECO-011 — 64+ install skriptů bez individuálního registru

```yaml
id: GAP-ECO-011
severity: MEDIUM
description: "SPOS-008 katalogizoval skripty jako celek (Termux stubs), ale individuální SCRIPT_REGISTRY neexistuje."
recommendation: "Vytvořit SCRIPT_REGISTRY nebo odkázat na SPOS-008 DEPLOYMENT_ARCHITECTURE"
effort: S
```

### GAP-ECO-012 — project_snapshot.md drift

```yaml
id: GAP-ECO-012
severity: MEDIUM
description: "project_snapshot.md byl historicky zastaralý (v0.4.0 vs v0.6.0). Aktualizováno SPOS-015, ale žádný mechanismus automatické aktualizace neexistuje."
recommendation: "Přidat do CI nebo post-commit hook"
effort: M
```

---

## NÍZKÉ GAPY

### GAP-ECO-013 — platform/data/ nedokumentováno

```yaml
id: GAP-ECO-013
severity: LOW
description: "platform/data/ obsahuje starcore.db (SQLite). Adresář je runtime artifact, ale nie je v .gitignore."
recommendation: "Ověřit .gitignore coverage"
effort: XS
```

### GAP-ECO-014 — platform/site/ v repozitáři

```yaml
id: GAP-ECO-014
severity: LOW
description: "platform/site/ je MkDocs build output. Měl by být v .gitignore."
recommendation: "Přidat do .gitignore, smazat z git history"
effort: XS
```

### GAP-ECO-015 — tools/ Termux stubs bez README

```yaml
id: GAP-ECO-015
severity: LOW
description: "tools/ (18 Termux shell script stubs) nemá README vysvětlující stav."
recommendation: "Přidat README.md nebo archivovat"
effort: XS
```
