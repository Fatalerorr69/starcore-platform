# AUDIT REGISTRY

Standard: SPOS-005 §5 | Aktualizováno: 2026-08-06

Audit Engine **z velké části již existoval** (`platform/.starcore/scripts/qc_engine.py` + CI toolchain) — audit potvrdil pokrytí 6 ze 7 domén (A01-A07). Adoptováno a doplněno, ne duplikováno.

---

## AUDIT DOMAINS

### A01 — Repository Audit
```yaml
audit_id: A01
name: Repository Structure Audit
domain: Repository
tool: "manuální (SES-001 gap analýza) + regression_sentinel.py (workflow_count, config_fields)"
inputs: "adresářová struktura, MODULE_REGISTRY.md"
outputs: "SES-001-TECHNICAL-STANDARD.md gap analýza"
frequency: ON_DEMAND
status: ČÁSTEČNĚ AUTOMATIZOVÁNO
```

### A02 — Code Quality Audit
```yaml
audit_id: A02
name: Code Quality Audit
domain: Code
tool: "pytest, ruff, pyright"
inputs: "packages/, apps/, tests/"
outputs: "PASS/FAIL + coverage %"
frequency: "CI (každý PR) + ON_DEMAND"
status: AKTIVNÍ — ŽIVĚ OVĚŘENO (2026-08-06)
last_run: "796 passed, 9 skipped (postgres, expected), ruff 0 chyb, pyright 0 chyb"
```

### A03 — Security Audit
```yaml
audit_id: A03
name: Security Audit
domain: Security
tool: "bandit, pip-audit, gitleaks (CI only)"
inputs: "packages/, apps/, scripts/, dependencies"
outputs: "SAST findings, CVE list, secret scan"
frequency: "CI (každý PR) + nightly (security-nightly.yml) + ON_DEMAND"
status: AKTIVNÍ — ČÁSTEČNĚ ŽIVĚ OVĚŘENO
last_run: "bandit: 0 nálezů (-ll), pip-audit: 0 zranitelností. gitleaks NENÍ lokálně dostupný (jen GitHub Action) — needeno ověřit v tomto prostředí"
```

### A04 — Documentation Audit
```yaml
audit_id: A04
name: Documentation Audit
domain: Documentation
tool: "manuální (.claude/registry/DOCUMENTATION_REGISTRY.md) + regression_sentinel.py (adr_count)"
inputs: "docs/, README, ADR, registries"
outputs: "DOCUMENTATION_REGISTRY.md gap list"
frequency: ON_DEMAND
status: ČÁSTEČNĚ AUTOMATIZOVÁNO (SPOS-006 gap, viz SPOS_REGISTRY.md)
```

### A05 — Infrastructure Audit
```yaml
audit_id: A05
name: Infrastructure Audit
domain: Infrastructure
tool: "starcore doctor/diagnose (Docker), NEDOSTUPNÉ pro Proxmox v tomto prostředí"
inputs: "Docker daemon, Proxmox API (nedostupné)"
outputs: "diagnostics report"
frequency: ON_DEMAND
status: ČÁSTEČNÉ — Docker dostupný, Proxmox mimo dosah tohoto prostředí (viz INFRASTRUCTURE_REGISTRY.md)
```

### A06 — Dependency Audit
```yaml
audit_id: A06
name: Dependency Audit
domain: Dependencies
tool: "pip-audit, uv lock --check"
inputs: "pyproject.toml, uv.lock"
outputs: "CVE list, lock sync status"
frequency: "CI + nightly + ON_DEMAND"
status: AKTIVNÍ — ŽIVĚ OVĚŘENO
last_run: "0 zranitelností, uv.lock konzistentní"
```

### A07 — Architecture Audit
```yaml
audit_id: A07
name: Architecture Audit
domain: Architecture
tool: "release_readiness.py (GOVERNANCE gate) + ADR compliance + manuální SES-001 audit"
inputs: "docs/adr/, MODULE_REGISTRY.md, dependency graph"
outputs: "GOVERNANCE gate PASS/FAIL, MOD-010..015 audit TODO"
frequency: ON_DEMAND
status: AKTIVNÍ — GOVERNANCE gate PASS, ale MOD-010..015 (ecosystem moduly) stále nedokumentovány (existující SES-001 gap)
```

---

## STATISTIKY

```yaml
domains_total: 7
domains_fully_automated: 3   # A02, A03(částečně), A06
domains_partial: 4           # A01, A04, A05, A07
last_full_audit: 2026-08-06
```

Detail posledního běhu: `.claude/reports/FIRST_FULL_AUDIT_REPORT.md`
