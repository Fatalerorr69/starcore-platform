# SECURITY BASELINE

Standard: SPOS-009 §12 | Aktualizováno: 2026-08-07

Minimální požadované bezpečnostní kontroly pro STARCORE platformu. Dokument definuje, co musí platit pro každý production deployment.

---

## MODEL: PREVENT → DETECT → ANALYZE → RESPOND → RECOVER

---

## REQUIRED CONTROLS

### C01 — Secrets Never in Code

```yaml
control_id: C01
description: "Žádný secret, API klíč ani token nesmí být commitován do repozitáře"
validation:
  - gitleaks CI scan na každý push (starcore-security.yml) ✅
  - pip-audit pro detekci kompromitovaných závislostí ✅
  - .gitignore pokrývá .env soubory ✅
status: SPLNĚNO
exceptions: []
```

### C02 — Dependency Vulnerability Scanning

```yaml
control_id: C02
description: "Všechny Python závislosti musí projít CVE scanem před nasazením"
validation:
  - pip-audit v CI pipeline ✅
  - uv.lock pin-based (reproducible builds) ✅
  - Dependabot config EXISTS (platform/.github/dependabot.yml) ale GitHub ho NEČTE ⚠️
status: ČÁSTEČNĚ_SPLNĚNO
exceptions:
  - "Dependabot alerts neaktivní (config v orphaned platform/.github/, ne root .github/)"
  - "Riziko přijato: pip-audit v CI kompenzuje"
risk_acceptance:
  accepted_by: SPOS-009 Security Audit 2026-08-07
  rationale: "pip-audit poskytuje ekvivalentní ochranu; Dependabot přesun je doporučen (SFIND-002)"
```

### C03 — Static Code Analysis

```yaml
control_id: C03
description: "Kód musí projít bandit (bezpečnostní analýza) a ruff (linting)"
validation:
  - bandit -r packages/ apps/ scripts/ -ll -q → 0 findings ✅
  - ruff check . → All checks passed ✅
  - Obě integrovány do CI (ci.yml) ✅
status: SPLNĚNO
exceptions: []
```

### C04 — Type Safety

```yaml
control_id: C04
description: "Kód musí projít pyright strict type checking"
validation:
  - pyright → 0 errors ✅
status: SPLNĚNO
exceptions: []
```

### C05 — API Authentication

```yaml
control_id: C05
description: "Všechna API volání musí být autentizována (X-API-Key)"
validation:
  - platform/packages/auth/ implementuje X-API-Key middleware ✅
  - ADR-012: Single API key model (záměrné pro homelab scope) ✅
  - ADR-008: Security architecture dokumentována ✅
status: SPLNĚNO
exceptions:
  - "Health check endpoint (/health) je veřejný — záměrné (monitoring)"
```

### C06 — AI Provider Credentials via Environment Variables Only

```yaml
control_id: C06
description: "AI provider credentials (Anthropic, OpenAI-compatible) musí být čteny z env proměnných"
validation:
  - STARCORE_ANTHROPIC_API_KEY čten z env ✅
  - Žádný klíč v kódu ani v .claude/ dokumentech ✅
  - Pydantic validace AI provider inputů (prompt injection mitigace) ✅
status: SPLNĚNO
exceptions: []
```

### C07 — CI Gate Must Pass Before Merge

```yaml
control_id: C07
description: "Všechny CI kontroly musí projít před merge do main"
validation:
  - ci.yml: pytest + ruff + pyright + bandit + pip-audit ✅
  - Branch protection: NEOVĚŘENO (vyžaduje gh API admin přístup, nedostupné)
status: ČÁSTEČNĚ_SPLNĚNO
exceptions:
  - "GitHub branch protection rules neověřeny z tohoto prostředí"
risk_acceptance:
  accepted_by: SPOS-009 Security Audit 2026-08-07
  rationale: "CI toolchain je funkční a ověřený; branch protection je administrativní vrstva"
```

### C08 — Workflow Permissions Principle of Least Privilege

```yaml
control_id: C08
description: "GitHub Actions workflows musí mít explicitní, minimální permissions blok"
validation:
  - root .github/workflows/*.yml: 5/6 souborů BEZ explicitního permissions bloku ⚠️
  - Výjimka: release.yml (má permissions) ✅
  - Zbývající 4 workflow soubory běží s implicitními oprávněními
status: NESPLNĚNO
findings: [SFIND-001]
remediation:
  action: "Přidat 'permissions: {contents: read}' do ci.yml, starcore-security.yml, starcore-integrity.yml"
  priority: STŘEDNÍ
  blocking: false
```

---

## COMPLIANCE SCORE

```yaml
total_controls: 8
passed: 5 (C01, C03, C04, C05, C06)
partially_passed: 2 (C02, C07)
failed: 1 (C08)
compliance_score: "62.5% fully compliant (5/8), 87.5% partially compliant (7/8)"
overall_assessment: ČÁSTEČNĚ_VYHOVUJÍCÍ
last_calculated: "2026-08-07"
```

---

## RISK ACCEPTANCE LOG

| ID | Riziko | Přijal | Datum | Podmínka revize |
|---|---|---|---|---|
| RA-001 | Dependabot neaktivní (C02 partial) | SPOS-009 | 2026-08-07 | Revize při přesunu na produkci |
| RA-002 | Branch protection neověřena (C07 partial) | SPOS-009 | 2026-08-07 | Revize při zřízení GitHub admin přístupu |
| RA-003 | Workflow permissions chybí (C08 fail) | N/A — OTEVŘENÝ NÁLEZ | 2026-08-07 | Implementovat při nejbližší CI update |

---

## VÝJIMKY (EXCEPTIONS)

| Výjimka | Zdůvodnění | Platnost |
|---|---|---|
| Health endpoint bez auth | Monitoring vyžaduje veřejný health check (ADR-012) | Trvalá |
| Single API key model | Homelab scope, ne enterprise (ADR-012) | Do škálování |
| SBOM negenerován | cosign/sbom-action config orphaned; pip-audit kompenzuje | Do přesunutí do root .github/ |

---

## PROXMOX SECURITY BASELINE (připraveno, neověřeno)

```yaml
status: PŘIPRAVENO — Proxmox nedostupný z tohoto prostředí

required_controls:
  - OS updates: automatické security patches
  - Firewall: pouze nutné porty (8006 API, 22 SSH, 443 services)
  - Users: min. 2 adminy, zakázat root login přes SSH
  - Certificates: Let's Encrypt nebo interní CA
  - Backups: daily PBS (Proxmox Backup Server) snapshots
  - SSH: key-based auth only, zakázat password auth
  - API tokens: per-task tokens s minimálními právy (ADR-012 princip)
```

---

## DOCKER SECURITY BASELINE (připraveno, neověřeno)

```yaml
status: PŘIPRAVENO — Docker daemon neběží v tomto prostředí

required_controls:
  - Images: pinovat na digest nebo konkrétní tag (ne :latest)
  - Privileges: no --privileged containers
  - Volumes: read-only kde možné
  - Networks: per-service network isolation (docker-compose.yml základ existuje)
  - Capabilities: drop ALL, přidat jen nutné
  - User: ne root uvnitř kontejneru (non-root user v Dockerfile)
  - Scanning: trivy nebo grype v CI po buildu image
```
