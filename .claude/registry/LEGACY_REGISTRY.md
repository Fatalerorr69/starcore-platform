# LEGACY REGISTRY

Standard: SPOS-015 §4 | Aktualizováno: 2026-08-07

Registr legacy adresářů a komponent z předchozích verzí STARCORE (6.x/7.x/8.x). Žádný z těchto adresářů není importován ani použit živým platform/ kódem.

---

## FORMÁT

```yaml
id: LEG-XXX
directory: ""
version_origin: "6.x|7.x|8.x|unknown"
file_count: N
type: "LEGACY|STUB|DEAD|EMPTY"
termux_refs: true|false
imported_by: []
recommendation: "ARCHIVE|DELETE|DOCUMENT|KEEP"
```

---

## LEGACY ADRESÁŘE

### LEG-001 — core/

```yaml
id: LEG-001
directory: core/
version_origin: "6.x-7.x"
file_count: 43
type: LEGACY
termux_refs: false
subdirectories: [bin/, cli/, config/, database/, installer/, lib/, logging/, modules/, plugins/, runtime/, services/, utils/]
imported_by: []
description: "Rozsáhlý Python package z předchozí architektury. Obsahuje vlastní CLI, config loader, database layer, plugin system, logging. Kompletně nahrazen platform/packages/."
recommendation: ARCHIVE
```

### LEG-002 — control_center/

```yaml
id: LEG-002
directory: control_center/
version_origin: "7.x"
file_count: 21
type: LEGACY
termux_refs: false
subdirectories: [backups/, bin/, config/, modules/]
imported_by: []
description: "Legacy control center s backup managementem, konfigurací a 6 moduly. Funkce nahrazena platform/ CLI a API."
recommendation: ARCHIVE
```

### LEG-003 — mission_engine/

```yaml
id: LEG-003
directory: mission_engine/
version_origin: "7.x"
file_count: 3
type: LEGACY
termux_refs: false
subdirectories: [execution/, missions/, workflows/]
imported_by: []
description: "Workflow/mission orchestration engine. Funkce nahrazena platform/packages/orchestrator/."
recommendation: ARCHIVE
```

### LEG-004 — studio/

```yaml
id: LEG-004
directory: studio/
version_origin: "7.x"
file_count: 3
type: LEGACY
termux_refs: false
subdirectories: [dashboard/, module_control/, system_view/]
imported_by: []
description: "Legacy dashboard a system view UI. Funkce nahrazena platform/ FastAPI UI (/ui endpoint)."
recommendation: ARCHIVE
```

### LEG-005 — sdk/

```yaml
id: LEG-005
directory: sdk/
version_origin: "7.x"
file_count: 4
type: LEGACY
termux_refs: false
subdirectories: [core/]
imported_by: []
description: "Legacy SDK pro STARCORE extensions. Funkce nahrazena platform/packages/provider_sdk/."
recommendation: ARCHIVE
```

### LEG-006 — hardening/

```yaml
id: LEG-006
directory: hardening/
version_origin: "7.x-8.x"
file_count: 2
type: LEGACY
termux_refs: false
subdirectories: [dependencies/, environment/]
imported_by: []
description: "Security hardening skripty: dependency_manager.py, environment_audit.py. Funkce nahrazena platform/ CI gates (pip-audit, bandit)."
recommendation: ARCHIVE
```

### LEG-007 — cli/

```yaml
id: LEG-007
directory: cli/
version_origin: "6.x-7.x"
file_count: "unknown"
type: LEGACY
termux_refs: false
subdirectories: [starcore/]
imported_by: []
description: "Předchůdce platform/apps/cli/. Legacy CLI package."
recommendation: ARCHIVE
```

### LEG-008 — config/

```yaml
id: LEG-008
directory: config/
version_origin: "7.x"
file_count: 5
type: LEGACY
termux_refs: false
files: [ai.json, ai_context.yaml, platform.json, runtime.json, security.json]
imported_by: []
description: "Statické JSON/YAML konfigurace. Platform/ používá pydantic-settings s env vars (STARCORE_* prefix)."
recommendation: ARCHIVE
```

### LEG-009 — bin/

```yaml
id: LEG-009
directory: bin/
version_origin: "7.x"
file_count: 4
type: LEGACY
termux_refs: true (control-center symlink → Termux path)
files: [starcore, starcore-status, starcore-verify, control-center (broken symlink)]
imported_by: []
description: "Legacy CLI entry points. Platform/ používá uv run starcore."
recommendation: ARCHIVE
```

### LEG-010 — plugins/ (root)

```yaml
id: LEG-010
directory: plugins/
version_origin: "7.x"
file_count: "unknown"
type: LEGACY
termux_refs: false
subdirectories: [enabled/, registry/]
imported_by: []
description: "Root-level plugin system. Živý plugin system je v platform/plugins/."
recommendation: ARCHIVE
```

### LEG-011 — sessions/ (root)

```yaml
id: LEG-011
directory: sessions/
version_origin: "7.x"
file_count: 1
type: LEGACY
termux_refs: false
files: [session_memory.json]
imported_by: []
description: "Legacy session memory. Živý session management je v platform/.starcore/sessions/."
recommendation: ARCHIVE
```

### LEG-012 — prompts/ (root)

```yaml
id: LEG-012
directory: prompts/
version_origin: "7.x-8.x"
file_count: 4
type: LEGACY
termux_refs: true (generated/audit.md)
files: [master_context.md, proxmox_operator.md, repository_audit.md, generated/audit.md]
imported_by: []
description: "Legacy prompts. Živý prompt registry je v platform/.starcore/prompts/registry.yaml."
recommendation: ARCHIVE
```

### LEG-013 — backups/

```yaml
id: LEG-013
directory: backups/
version_origin: "7.x"
file_count: "unknown"
type: LEGACY
termux_refs: false
subdirectories: [releases/]
imported_by: []
description: "Legacy backup/release adresář."
recommendation: ARCHIVE
```

### LEG-014 — installers/

```yaml
id: LEG-014
directory: installers/
version_origin: "8.x"
file_count: "unknown"
type: LEGACY
termux_refs: false
subdirectories: [android/]
imported_by: []
description: "Android/Termux instalační skripty."
recommendation: ARCHIVE
```

### LEG-015 — templates/

```yaml
id: LEG-015
directory: templates/
version_origin: "7.x"
file_count: "unknown"
type: LEGACY
termux_refs: false
subdirectories: [module_template/]
imported_by: []
description: "Module scaffolding template."
recommendation: ARCHIVE
```

### LEG-016 — bundles_7x/

```yaml
id: LEG-016
directory: bundles_7x/
version_origin: "7.x"
file_count: 5
type: LEGACY
termux_refs: false
files: [install_7_3_4_*.sh, install_7_5_6_*.sh, install_7_7_8_*.sh, install_7_9_10_*.sh, run_7x_bulk_suite.sh]
imported_by: []
description: "Batch install bundly pro STARCORE 7.x sérii."
recommendation: ARCHIVE
```

### LEG-017 — security/ (root)

```yaml
id: LEG-017
directory: security/
version_origin: "7.x-8.x"
file_count: 3+
type: LEGACY
termux_refs: false
files_notable: [backup_engine.py, github_intelligence_upgrade.py, security_audit.py]
imported_by: []
description: "Legacy security skripty. Neimportované platformou. Funkce nahrazena CI gates."
recommendation: ARCHIVE
```

### LEG-018 — intelligence/

```yaml
id: LEG-018
directory: intelligence/
version_origin: "7.x"
type: LEGACY
imported_by: []
recommendation: ARCHIVE
```

### LEG-019 — automation/ (root)

```yaml
id: LEG-019
directory: automation/
version_origin: "7.x"
type: LEGACY
imported_by: []
recommendation: ARCHIVE
```

---

## DEAD CODE

### DEAD-001 — github_intelligence/

```yaml
id: DEAD-001
directory: github_intelligence/
file: github_scanner.py
references: 0
imported_by: []
recommendation: DELETE
```

### DEAD-002 — knowledge_engine/

```yaml
id: DEAD-002
directory: knowledge_engine/
file: knowledge_core.py
references: 0 (zmíněn pouze v .starcore memory — žádný import)
imported_by: []
recommendation: DELETE
```

### DEAD-003 — performance/

```yaml
id: DEAD-003
directory: performance/
file: performance_analyzer.py
references: 0
imported_by: []
recommendation: DELETE
```

### DEAD-004 — api_gateway/

```yaml
id: DEAD-004
directory: api_gateway/
file: api_gateway.py
references: 0
imported_by: []
recommendation: DELETE
```

---

## EMPTY REGISTRIES

### EMPTY-001 — registry/modules.json

```yaml
id: EMPTY-001
file: registry/modules.json
content: '{"modules": []}'
recommendation: DELETE_OR_POPULATE
```

### EMPTY-002 — registry/sdk_registry.json

```yaml
id: EMPTY-002
file: registry/sdk_registry.json
content: empty
recommendation: DELETE_OR_POPULATE
```

### EMPTY-003 — runtime/marketplace/registry.json

```yaml
id: EMPTY-003
file: runtime/marketplace/registry.json
content: '{"plugins": []}'
recommendation: DELETE_OR_POPULATE
```

---

## STATISTIKY

```yaml
total_legacy_entries: 19
total_dead_code: 4
total_empty_registries: 3
recommendation_archive: 19
recommendation_delete: 4
recommendation_delete_or_populate: 3
```
