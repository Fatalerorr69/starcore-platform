# ECOSYSTEM RECOMMENDATIONS

Standard: SPOS-015 §10 | Aktualizováno: 2026-08-07

Doporučení pro zlepšení ekosystémového zdraví na základě ECOSYSTEM_GAP_ANALYSIS.

---

## SUMMARY

```yaml
total_recommendations: 12
effort_xs: 5
effort_s: 4
effort_m: 2
effort_l: 1
projected_improvement: "Ecosystem 58% → 75%+"
```

---

## SPRINT 1 — QUICK WINS (XS, < 30 min každé)

### REC-ECO-01: Smazat dead code adresáře

```yaml
id: REC-ECO-01
gap: GAP-ECO-002
effort: XS
impact: "Dead Code 20% → 50%"
action: "Smazat github_intelligence/, knowledge_engine/, performance/, api_gateway/"
risk: NONE (zero references verified)
```

### REC-ECO-02: Smazat prázdné registry

```yaml
id: REC-ECO-02
gap: GAP-ECO-003
effort: XS
impact: "Repository Hygiene 35% → 38%"
action: "Smazat registry/modules.json, registry/sdk_registry.json, runtime/marketplace/registry.json"
risk: NONE (prázdný obsah)
```

### REC-ECO-03: Smazat broken Termux symlink

```yaml
id: REC-ECO-03
gap: GAP-ECO-006
effort: XS
impact: "Hygiene improvement"
action: "Smazat bin/control-center symlink"
risk: NONE (broken outside Termux)
```

### REC-ECO-04: Extrahovat _persist_run()

```yaml
id: REC-ECO-04
gap: GAP-ECO-009
effort: XS
impact: "DRY kód"
action: "Přesunout _persist_run() do packages/core/run_persistence.py, importovat z obou routerů"
risk: LOW (existující testy pokryjí)
```

### REC-ECO-05: Dokumentovat platform/scripts/

```yaml
id: REC-ECO-05
gap: GAP-ECO-008
effort: XS
impact: "Script coverage 57% → 100%"
action: "Přidat make-executable.sh, quickstart.sh, release.py do DEPLOYMENT_REGISTRY nebo AUTOMATION_REGISTRY"
risk: NONE
```

---

## SPRINT 2 — SMALL IMPROVEMENTS (S, < 2h každé)

### REC-ECO-06: Aktualizovat root README.md

```yaml
id: REC-ECO-06
gap: GAP-ECO-004
effort: S
impact: "Onboarding improvement"
action: "Přidat sekci Repository Structure s klasifikací ACTIVE/LEGACY/STUB nebo odkaz na ECOSYSTEM_MAP.md"
risk: NONE
```

### REC-ECO-07: Přesunout platform/.github/ workflows

```yaml
id: REC-ECO-07
gap: GAP-ECO-005
effort: S
impact: "Automation 61% → 65%, opraví orphaned CI"
action: "Přesunout relevantní workflows do root .github/ nebo smazat duplicity"
risk: LOW (CI changes — test first)
```

### REC-ECO-08: Katalogizovat platform/reports/

```yaml
id: REC-ECO-08
gap: GAP-ECO-007
effort: S
impact: "Governance coverage improvement"
action: "Katalogizovat 12 reportů do DOCUMENTATION_REGISTRY nebo archivovat"
risk: NONE
```

### REC-ECO-09: Vytvořit ADR-018 WebSocket Streaming

```yaml
id: REC-ECO-09
gap: GAP-ECO-010
effort: S
impact: "ADR coverage improvement"
action: "Dokumentovat design decision pro WebSocket blueprint execution"
risk: NONE
```

---

## SPRINT 3 — MEDIUM IMPROVEMENTS (M, < 1 den každé)

### REC-ECO-10: Archivovat legacy do legacy/ subdir

```yaml
id: REC-ECO-10
gap: GAP-ECO-001
effort: M
impact: "Repository Hygiene 35% → 55%, Legacy Management 15% → 50%"
action: |
  Vytvořit legacy/ adresář a přesunout:
  core/, control_center/, mission_engine/, studio/, sdk/, hardening/, cli/,
  config/, bin/, plugins/, sessions/, prompts/, backups/, installers/,
  templates/, security/, intelligence/, automation/, tools/, bundles_7x/
  Přidat legacy/README.md s vysvětlením.
risk: MEDIUM (git history zachována, ale paths se změní)
note: "Vyžaduje explicitní schválení uživatele — destruktivní reorganizace"
```

### REC-ECO-11: Automatická snapshot aktualizace

```yaml
id: REC-ECO-11
gap: GAP-ECO-012
effort: M
impact: "Eliminuje snapshot drift"
action: "Přidat post-commit hook nebo CI step pro aktualizaci project_snapshot.md klíčových metrik"
risk: LOW
```

---

## SPRINT 4 — STRATEGIC (L)

### REC-ECO-12: Repozitář split (monorepo cleanup)

```yaml
id: REC-ECO-12
gap: GAP-ECO-001
effort: L
impact: "Repository Hygiene 35% → 80%+"
action: |
  Zvážit oddělení legacy kódu do separátního repozitáře (starcore-legacy)
  a ponechání pouze platform/, .claude/, knowledge/, .github/ v hlavním repo.
risk: HIGH (vyžaduje pečlivé plánování, git history split)
note: "Strategické rozhodnutí — vyžaduje explicitní schválení"
```

---

## IMPLEMENTATION ROADMAP

```
Sprint 1 (XS): ECO health 58% → 62%
  └── REC-ECO-01..05 (~2h celkem)

Sprint 2 (S): ECO health 62% → 68%
  └── REC-ECO-06..09 (~8h celkem)

Sprint 3 (M): ECO health 68% → 75%
  └── REC-ECO-10..11 (~16h celkem)

Sprint 4 (L): ECO health 75% → 85%+
  └── REC-ECO-12 (~40h)
```
