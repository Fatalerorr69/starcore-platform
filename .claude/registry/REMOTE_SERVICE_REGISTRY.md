# REMOTE SERVICE REGISTRY

Standard: SPOS-007 §10 | Aktualizováno: 2026-08-06

Vzdálené služby, které STARCORE ekosystém aktivně používá nebo bude používat.

---

### REMOTE-001 — GitHub
```yaml
service: GitHub
purpose: "Zdrojový repozitář, CI/CD (GitHub Actions), issue tracking"
repo: "Fatalerorr69/starcore-platform"
status: AKTIVNÍ — ŽIVĚ OVĚŘENO (git push úspěšný v každém SPOS kroku této session)
auth: "git credentials (spravováno hostitelským prostředím Claude Code Remote)"
```

### REMOTE-002 — Anthropic (Claude API)
```yaml
service: Anthropic Claude API
purpose: "AI Blueprint Generation (platform/packages/ai) + AI Engineering Agent operátor (toto prostředí)"
status: AKTIVNÍ (operátor — tato session; blueprint generace — volitelná, vyžaduje STARCORE_ANTHROPIC_API_KEY)
auth: "STARCORE_ANTHROPIC_API_KEY (aplikace) / spravováno hostitelem (tato session)"
```

### REMOTE-003 — Proxmox API (cílový)
```yaml
service: Proxmox VE API
purpose: "Infrastructure provisioning (VM/LXC)"
status: NAKONFIGUROVÁNO V KÓDU, NEDOSTUPNÉ Z TOHOTO PROSTŘEDÍ
auth: "STARCORE_PROXMOX_HOST/USER/TOKEN_NAME/TOKEN_VALUE — chybí"
```

### REMOTE-004 — OpenAI-compatible endpoint (volitelné)
```yaml
service: "OpenAI-compatible (Ollama/vLLM/LM Studio/LocalAI)"
purpose: "Alternativní AI Provider"
status: PLÁNOVÁNO (vyžaduje self-hosted Ollama na AI Core VM)
auth: "STARCORE_AI_BASE_URL, STARCORE_AI_MODEL, STARCORE_AI_API_KEY (volitelné)"
```

---

## OSTATNÍ MCP KONEKTORY (toto Claude Code prostředí, mimo STARCORE aplikaci samotnou)

Toto prostředí má přístup k desítkám MCP konektorů (Slack, Notion, Linear, Google Drive, atd.) — nejsou součástí STARCORE Platform architektury, jsou to nástroje AI operátora (tato session). Nezahrnuto do STARCORE infrastrukturního modelu.

---

## STATISTIKY

```yaml
remote_services_total: 4
active: 2
configured_unreachable: 1
planned: 1
```
