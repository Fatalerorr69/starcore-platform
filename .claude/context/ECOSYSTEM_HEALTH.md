# ECOSYSTEM HEALTH

Standard: SPOS-015 §8 | Aktualizováno: 2026-08-07

Celkový health score STARCORE ekosystému — agregace všech SPOS health dimenzí + nová ekosystémová vrstva.

---

## ECOSYSTEM HEALTH SCORE

```
╔═══════════════════════════════════════════════════════════╗
║           ECOSYSTEM HEALTH SCORE: 58%                    ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  PLATFORM HEALTH (živý kód)                               ║
║  ─────────────────────────────                            ║
║  Code Quality:          95%  VÝBORNÝ (ruff/pyright/100%)  ║
║  Test Coverage:        100%  VÝBORNÝ                      ║
║  Security (CI):         90%  DOBRÝ (bandit/pip-audit/gl)  ║
║  Documentation:         80%  DOBRÝ (mkdocs --strict PASS) ║
║  Intelligence (QC):     88%  DOBRÝ (4 engines)            ║
║  Integration:           64%  ČÁSTEČNÝ                     ║
║  Automation:            61%  ČÁSTEČNÝ                     ║
║  AAOS (AI):             38%  KRITICKÝ                     ║
║                                                           ║
║  ECOSYSTEM HEALTH (celý repozitář)                        ║
║  ─────────────────────────────────                        ║
║  Repository Hygiene:    35%  KRITICKÝ                     ║
║  Legacy Management:     15%  KRITICKÝ                     ║
║  Dead Code:             20%  KRITICKÝ                     ║
║  Governance Coverage:   60%  ČÁSTEČNÝ                     ║
║                                                           ║
╠═══════════════════════════════════════════════════════════╣
║  Platform Maturity:      ~77%  (DOBRÝ)                    ║
║  Ecosystem Maturity:     ~33%  (KRITICKÝ)                 ║
║  Combined Score:         ~58%  (ČÁSTEČNĚ_ZDRAVÝ)          ║
╚═══════════════════════════════════════════════════════════╝
```

---

## DIMENZE DETAIL

### Repository Hygiene: 35%

**Pozitiva:**
- platform/ čistě strukturovaný monolith
- .claude/ governance vrstva kompletní (SES/SAKB/SPOS-001..014)
- .github/ CI workflows funkční

**Negativa:**
- 18 legacy adresářů bez governance (-30%)
- 4 dead code adresáře (-10%)
- 3 prázdné registry (-5%)
- 64+ nezdokumentovaných install skriptů (-10%)
- Broken Termux symlink v bin/ (-5%)
- platform/reports/ orphaned (-5%)

### Legacy Management: 15%

**Pozitiva:**
- SPOS-008 identifikoval 65 install skriptů jako Termux stubs
- SPOS-014 identifikoval 27 stub agentů

**Negativa:**
- 18 legacy adresářů nemá žádnou formální klasifikaci (-40%)
- Žádný archivační plán (-20%)
- core/ (43 souborů) a control_center/ (21 souborů) neadresovány (-15%)
- Žádný migration guide z legacy→platform (-10%)

### Dead Code: 20%

**Pozitiva:**
- Žádný dead code v platform/ (čistý)
- Dead code identifikován a katalogizován (SPOS-015)

**Negativa:**
- 4 dead code adresáře stále v repozitáři (-30%)
- 7 dead .py souborů (root-level) (-20%)
- Prázdné registry (modules.json, sdk_registry.json) stále přítomny (-15%)
- Neexistuje automatická detekce dead code (-15%)

### Governance Coverage: 60%

**Pozitiva:**
- platform/ plně pokryto (SPOS-001..014) (+30%)
- knowledge/ částečně pokryto (SAKB-000) (+5%)
- Stub agenti dokumentováni (SPOS-014) (+10%)
- Install skripty katalogizovány (SPOS-008) (+5%)
- Ekosystém nově zmapován (SPOS-015) (+10%)

**Negativa:**
- 18 legacy adresářů bez governance (-25%)
- Root-level skripty bez individuálního registru (-10%)
- platform/scripts/ 3/7 nedokumentovaných (-5%)

---

## HEALTH SCORE SROVNÁNÍ

| Dimenze | Score | Trend | SPOS |
|---|---|---|---|
| Code Quality | 95% | ═ | SPOS-005 |
| Test Coverage | 100% | ═ | SPOS-005 |
| Security | 90% | ═ | SPOS-009 |
| Documentation | 80% | ═ | SPOS-006 |
| Intelligence | 88% | ═ | SPOS-004 |
| Integration | 64% | ═ | SPOS-012 |
| Automation | 61% | ═ | SPOS-013 |
| AAOS (AI) | 38% | ═ | SPOS-014 |
| **Repository Hygiene** | **35%** | **NEW** | **SPOS-015** |
| **Legacy Management** | **15%** | **NEW** | **SPOS-015** |
| **Dead Code** | **20%** | **NEW** | **SPOS-015** |
| **Governance Coverage** | **60%** | **▲ +10%** | **SPOS-015** |

---

## QUICK ACTION TABLE

| Akce | Effort | Dopad na Score |
|---|---|---|
| Smazat 4 dead code adresáře | XS | Dead Code 20%→50% |
| Smazat 3 prázdné registry | XS | Repository Hygiene 35%→40% |
| Přidat LEGACY_README.md do 18 legacy dirs | S | Legacy Management 15%→35% |
| Archivovat legacy do legacy/ subdir | M | Repository Hygiene 35%→55%, Legacy 15%→50% |
| Přesunout orphaned platform/.github/ | S | Automation 61%→65% |
