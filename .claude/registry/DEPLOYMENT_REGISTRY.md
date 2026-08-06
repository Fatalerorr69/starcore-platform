# DEPLOYMENT REGISTRY

Standard: SPOS-008 §9 | Aktualizováno: 2026-08-06

---

### DEPLOY-001 — Docker Image Publish (definováno, ale NEAKTIVNÍ)
```yaml
deployment_id: DEPLOY-001
target: "Docker registry (GitHub Container Registry, dle docker-publish.yml)"
version: "platform v0.6.0"
date: NIKDY NESPUŠTĚNO
components: [platform Docker image]
status: KONFIGUROVÁNO, NEAKTIVNÍ — docker-publish.yml existuje jen v platform/.github/workflows/,
  které GitHub nečte (viz SES-001 oprava, orphaned config)
validation: N/A — nikdy nespuštěno
```

### DEPLOY-002 — CI Test/Lint/Security Gate (AKTIVNÍ)
```yaml
deployment_id: DEPLOY-002
target: "GitHub Actions (root .github/workflows/ci.yml)"
version: "kontinuální, každý push/PR"
date: "průběžně, naposledy živě ověřeno 2026-08-06 (SPOS-005)"
components: [pytest, ruff, pyright, bandit, pip-audit, alembic check, mkdocs build --strict]
status: AKTIVNÍ
validation: "796 passed, 0 failed; ruff/pyright/bandit/pip-audit čisté (viz FIRST_FULL_AUDIT_REPORT.md)"
```

### DEPLOY-003 — Proxmox VM Provisioning (PLÁNOVÁNO)
```yaml
deployment_id: DEPLOY-003
target: "Proxmox VE (HOST-002, nedostupný)"
version: N/A
date: NIKDY NESPUŠTĚNO
components: [VM-101 ai-core, VM-102 database, VM-103 monitoring]
status: PLÁNOVÁNO — blokováno nedostupností Proxmox z tohoto prostředí
validation: N/A
```

### DEPLOY-004 — Termux/Android Edge Bootstrap (HISTORICKÉ, NEPRODUKČNÍ)
```yaml
deployment_id: DEPLOY-004
target: "Android/Termux (65 install_*.sh skriptů)"
version: "generace 6BX..8J"
date: "neznámé (předchozí sessions)"
components: "stub Python soubory, adresářová struktura — NE funkční služby"
status: HISTORICKÉ — negenerativní produkční hodnota, viz DEPLOYMENT_ARCHITECTURE.md Track B
validation: NEAPLIKOVATELNÉ — skripty negenerují testovatelný, funkční kód
```

---

## STATISTIKY

```yaml
deployments_total: 4
active: 1 (DEPLOY-002, CI gate)
configured_inactive: 1 (DEPLOY-001, orphaned docker-publish)
planned: 1 (DEPLOY-003, Proxmox)
historical_nonproduction: 1 (DEPLOY-004, Termux stubs)
```
