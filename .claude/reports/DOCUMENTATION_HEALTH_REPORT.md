# DOCUMENTATION HEALTH REPORT

Standard: SPOS-006 §6, §18 | Datum: 2026-08-06

---

## D001 — MISSING DOCUMENTATION

| Nález | Závažnost | Detail |
|---|---|---|
| MOD-010..015 bez dokumentace | STŘEDNÍ | Existující ze SES-001 (agents/, knowledge/, security/, intelligence/, control_center/, ai_core/) |
| STARCORE Installation Manual (§10) | VYSOKÁ | Nevytvořeno — Proxmox prep, VM creation, Docker deployment, AI stack, Android Edge Node, backup/recovery |
| Infrastructure detailní docs (§11) | STŘEDNÍ | Proxmox host/VM topology/network/storage/GPU nedokumentováno (Proxmox nedostupný v tomto prostředí) |
| USER_GUIDE (§13) | STŘEDNÍ | Nevytvořeno — pro admin/dev/AI operátora/uživatele |
| `docker/ai-stack/README.md` | STŘEDNÍ | Existující gap z Bootstrap 00 |

## D002 — BROKEN LINKS

| Nález | Závažnost | Detail |
|---|---|---|
| Neprovedena plná linková kontrola | NÍZKÁ | `mkdocs build --strict` prošel (exit 0) — to ověřuje interní MkDocs odkazy v `platform/docs/`, ale nekontroluje odkazy uvnitř `.claude/` (mimo mkdocs scope) |

## D003 — OUTDATED DOCUMENTS

| Dokument | Závažnost | Detail |
|---|---|---|
| `platform/.starcore/memory/project_snapshot.md` | STŘEDNÍ | v0.4.0 vs. realita v0.6.0 (existující ze SPOS-001) |
| `platform/.starcore/state/release.md` | STŘEDNÍ | v0.2.0 vs. realita v0.6.0 (existující ze SPOS-001) |
| `platform/.starcore/memory/pending_work.md` | NÍZKÁ | Poslední aktualizace 2026-08-01, mnoho položek CLOSED ale ne všechny reflektují aktuální stav |

## D004 — DUPLICATE DOCUMENTS

| Nález | Závažnost | Detail |
|---|---|---|
| `platform/docs/ses/SES-0000-MASTER-INDEX.md` vs `.claude/ses/SES-000-*.md` | STŘEDNÍ | Podobné názvy (SES-0000 vs SES-000), zcela odlišný obsah a autor (ChatGPT vs. tato Claude Code session) — riziko záměny, viz `DOCUMENTATION_MAP.md` |

## D005 — MISSING REFERENCES

| Nález | Závažnost | Detail |
|---|---|---|
| `ADR-017-plugin-operator-controls.md` chybí v `mkdocs.yml` nav | NÍZKÁ | Zjištěno živě přes `mkdocs build --strict` (INFO úroveň, nefailuje build) |
| `knowledge/` dokumenty nebyly v `DOCUMENTATION_REGISTRY.md` explicitně vypsány jednotlivě | NÍZKÁ | Souhrnně zmíněny přes `KNOWLEDGE_REGISTRY.md`, ne duplicitně — akceptovatelné, ne oprava |

## D006 — REGISTRY MISMATCH

| Kontrola | Výsledek |
|---|---|
| Všechny `.claude/reports/*.md` mají záznam v `DOCUMENTATION_REGISTRY.md`? | ✅ ANO (ověřeno počtem: 20 reportů v `.claude/reports/`, všechny SES/SAKB/SPOS/DR záznamy accounted for) |
| Všechny `.claude/registry/*.md` jsou samy o sobě zaregistrované? | ⚠️ ČÁSTEČNĚ — `DOCUMENTATION_REGISTRY.md` netrackuje ostatní registry jako dokumenty samy o sobě (meta-mezera, nízké riziko) |

---

## ŽIVĚ OVĚŘENO

```
$ uv run mkdocs build --strict
INFO — 1 stránka mimo nav (ADR-017)
Exit code: 0 (PASS)
```

---

## CODE ↔ DOC SYNC (§8)

| Modul | Kód | Dokumentace | Testy | Registry záznam |
|---|---|---|---|---|
| MOD-001..009 (platform core) | ✅ | ✅ | ✅ | ✅ |
| MOD-010 Agent Framework | ✅ | ❌ | ❌ | ✅ (jako gap) |
| MOD-011 Knowledge Base | ✅ | ⚠️ (SAKB profily existují, ale ne vlastní kód `knowledge/core`) | ❌ | ✅ |
| MOD-012..015 | ✅ | ❌ | ❌ | ✅ (jako gap) |

---

## SOUHRN

```yaml
total_findings: 9
by_category:
  D001_missing: 5
  D002_broken_links: 1 (informational, not confirmed broken)
  D003_outdated: 3
  D004_duplicate: 1
  D005_missing_references: 2
  D006_registry_mismatch: 1
severity_high: 1
severity_medium: 6
severity_low: 4
mkdocs_strict: PASS
```
