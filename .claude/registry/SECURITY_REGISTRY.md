# SECURITY REGISTRY

Standard: SPOS-009 §5 | Aktualizováno: 2026-08-06

Audit potvrdil existující, funkční security kontroly v `platform/` (CI toolchain). Root `security/` adresář je **další Termux stub** (stejný vzorec jako `knowledge/core`, viz SAKB-000) — operuje nad `~/STARCORE` cestou, ne nad tímto repozitářem, žádná reálná bezpečnostní funkce.

---

## S01 — CODE SECURITY
```yaml
control_id: S01
domain: "Code Security"
tool: "bandit, pip-audit, gitleaks (CI-only)"
status: AKTIVNÍ — ŽIVĚ OVĚŘENO (SPOS-005, znovu potvrzeno zde)
last_check: "2026-08-06"
result: "bandit: 0 nálezů (-ll). pip-audit: 0 zranitelností. gitleaks: NEOVĚŘENO lokálně (binárka nedostupná), manuální grep na secret patterns v .claude/+knowledge/+.starcore/: 0 nálezů"
```

## S02 — SUPPLY CHAIN SECURITY
```yaml
control_id: S02
domain: "Supply Chain Security"
tool: "SBOM (cosign+sbom-action, ORPHANED), pip-audit, uv.lock"
status: ČÁSTEČNÉ — SBOM config existuje jen v platform/.github/ (orphaned, viz SES-001 finding)
last_check: "2026-08-06"
result: "uv.lock konzistentní. SBOM se negeneruje (docker-publish.yml, kde je cosign+sbom-action, není v aktivním root .github/workflows/)"
```

## S03 — INFRASTRUCTURE SECURITY
```yaml
control_id: S03
domain: "Infrastructure Security"
tool: "starcore diagnose (Proxmox/Docker health)"
status: NEOVĚŘITELNÉ — Proxmox nedostupný (chybí credentials), Docker daemon zde neběží (SPOS-007)
last_check: "2026-08-06"
result: "N/A — žádná reálná infrastruktura k prověření z tohoto prostředí"
```

## S04 — ACCESS CONTROL
```yaml
control_id: S04
domain: "Access Control"
tool: "X-API-Key (STARCORE Platform), git credentials (GitHub)"
status: AKTIVNÍ (aplikační vrstva), NEOVĚŘENO (GitHub branch protection — vyžaduje gh API/admin přístup, nedostupné)
last_check: "2026-08-06"
result: "Platform: single shared API key model (ADR-012, by design pro homelab). GitHub: branch protection rules NEOVĚŘENY (mimo dosah nástrojů této session)"
```

## S05 — AI SECURITY
```yaml
control_id: S05
domain: "AI Security"
tool: "STARCORE_ANTHROPIC_API_KEY (env var), AIProvider abstrakce"
status: AKTIVNÍ
last_check: "2026-08-06"
result: "API klíč čten z env, nikdy commitován. Prompt injection risk: negenerovaný blueprint YAML prochází Pydantic validací před použitím (mitigace). Data handling: žádná citlivá data v knowledge/ nebo .claude/"
```

---

## GITHUB SECURITY (§11, nový nález)

```yaml
finding: "Pouze 5/16 workflow souborů (root .github/ + platform/.github/) má explicitní 'permissions:' blok"
affected: "ci.yml (root, nejčastěji spouštěný), starcore-security.yml, starcore-integrity.yml nemají explicitní permissions"
risk: STŘEDNÍ — bez explicitního least-privilege permissions blocku běží GITHUB_TOKEN s defaultními (potenciálně širšími) právy repozitáře/organizace
recommendation: "Přidat 'permissions: {contents: read}' (nebo užší) do workflow souborů, které nepotřebují write přístup"
```

---

## STATISTIKY

```yaml
domains_total: 5 (S01-S05) + GitHub Security (§11)
domains_active: 3 (S01, S04 částečně, S05)
domains_partial: 1 (S02)
domains_unverifiable: 1 (S03 — no infra access)
new_findings: 1 (workflow permissions)
```
