# HYGIENE RECOMMENDATIONS

Standard: SPOS-018 | Aktualizováno: 2026-08-08

---

## DOPORUCENI

### P1 — Repository Restructure (Milestone 3)

1. Vytvorit `legacy/` adresarovou strukturu
2. Presunout 23 legacy dirs (agents/, ai_core/, ai_runtime/, automation/, autonomous/, backups/, bundles_7x/, cli/, config/, control_center/, core/, distributed/, hardening/, installers/, intelligence/, mission_engine/, plugins/, prompts/, runtime/, sdk/, security/, sessions/, studio/)
3. Presunout 65 install_*.sh do `legacy/termux-installers/`
4. Presunout templates/ do legacy/
5. Aktualizovat README.md directory tree
6. Overit CI green

### P2 — Code Quality (Milestone 4)

1. Deduplikovat _persist_run() (TD-008)
2. Odebrat psutil z primych deps (TD-009)
3. Overit CI green

### P3 — Optional Cleanup

1. Presunout platform/reports/ do legacy/ nebo .claude/reports/ (TD-010)
2. Git filter-branch pro 16MB Gold Master (TD-007)
