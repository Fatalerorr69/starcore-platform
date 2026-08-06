# SOURCE REGISTRY

Aktualizováno: 2026-08-06 | Standard: SAKB-000 §5

Formát: SOURCE_ID, NAME, TYPE, URL, OWNER, CATEGORY, VERSION, DATE_ADDED, LAST_REVIEW, TRUST_LEVEL, STATUS.

Trust levels dle SAKB-000 §9: L5 Official docs, L4 Verified technical source, L3 Community, L2 Unverified, L1 Experimental.

---

### SRC-PROXMOX-001
```yaml
name: Proxmox VE Documentation
type: Official Documentation
url: https://pve.proxmox.com/pve-docs/
owner: Proxmox Server Solutions GmbH
category: Infrastructure
version: 8.x
date_added: 2026-08-06
last_review: 2026-08-06
trust_level: L5
status: ACTIVE
```

### SRC-DOCKER-001
```yaml
name: Docker Documentation
type: Official Documentation
url: https://docs.docker.com/
owner: Docker Inc.
category: Infrastructure
version: 27.x
date_added: 2026-08-06
last_review: 2026-08-06
trust_level: L5
status: ACTIVE
```

### SRC-PYTHON-001
```yaml
name: Python Official Documentation
type: Official Documentation
url: https://docs.python.org/3/
owner: Python Software Foundation
category: Development
version: "3.12"
date_added: 2026-08-06
last_review: 2026-08-06
trust_level: L5
status: ACTIVE
```

### SRC-FASTAPI-001
```yaml
name: FastAPI Documentation
type: Official Documentation
url: https://fastapi.tiangolo.com/
owner: Sebastián Ramírez / tiangolo
category: Development
version: 0.116.x
date_added: 2026-08-06
last_review: 2026-08-06
trust_level: L5
status: ACTIVE
```

### SRC-OLLAMA-001
```yaml
name: Ollama Documentation
type: Official Documentation
url: https://github.com/ollama/ollama/blob/main/docs/
owner: Ollama Inc.
category: AI
version: latest
date_added: 2026-08-06
last_review: 2026-08-06
trust_level: L5
status: ACTIVE
```

### SRC-QDRANT-001
```yaml
name: Qdrant Documentation
type: Official Documentation
url: https://qdrant.tech/documentation/
owner: Qdrant
category: AI
version: latest
date_added: 2026-08-06
last_review: 2026-08-06
trust_level: L5
status: ACTIVE
```

### SRC-ANTHROPIC-001
```yaml
name: Anthropic / Claude API Documentation
type: Official Documentation
url: https://docs.claude.com/
owner: Anthropic
category: AI
version: current
date_added: 2026-08-06
last_review: 2026-08-06
trust_level: L5
status: ACTIVE
```

### SRC-GHACTIONS-001
```yaml
name: GitHub Actions Documentation
type: Official Documentation
url: https://docs.github.com/en/actions
owner: GitHub / Microsoft
category: Development
version: current
date_added: 2026-08-06
last_review: 2026-08-06
trust_level: L5
status: ACTIVE
```

### SRC-STARCORE-INTERNAL-001
```yaml
name: STARCORE Platform Repository (self)
type: Internal Codebase
url: (repo Fatalerorr69/starcore-platform, adresář platform/)
owner: Jakub Krajča
category: Project Knowledge
version: 0.6.0
date_added: 2026-08-06
last_review: 2026-08-06
trust_level: L5
status: ACTIVE
notes: Primární zdroj pravdy pro STARCORE Platform architekturu (ADR, README, testy)
```

---

## PLÁNOVANÉ ZDROJE (registrovat při dalším research cyklu)

| Source ID | Název | Kategorie |
|---|---|---|
| SRC-UBUNTU-001 | Ubuntu Server Documentation | Infrastructure |
| SRC-DEBIAN-001 | Debian Documentation | Infrastructure |
| SRC-K8S-001 | Kubernetes Documentation | Infrastructure |
| SRC-ANSIBLE-001 | Ansible Documentation | Infrastructure |
| SRC-TAILSCALE-001 | Tailscale Documentation | Infrastructure |
| SRC-OPENWEBUI-001 | OpenWebUI Documentation | AI |
| SRC-REDIS-001 | Redis Documentation | AI/Infrastructure |
| SRC-LANGCHAIN-001 | LangChain Documentation | AI |
| SRC-MCP-001 | Model Context Protocol Spec | AI |
| SRC-POSTGRES-001 | PostgreSQL Documentation | Development |
| SRC-TERMUX-001 | Termux Wiki | Edge |
| SRC-MAGISK-001 | Magisk Documentation | Edge |
