# Legacy Directory

This directory contains archived STARCORE components from versions 6.x through 8.x.

**None of these components are used by the active `platform/` codebase.**

They are preserved for historical reference and potential future migration.

## Contents

| Directory | Description | Origin |
|---|---|---|
| `termux-scripts/` | 68 Termux/Android install scripts | v6.x-8.x |
| `core/` | Legacy Python modules (v6.x-7.x) | Pre-platform |
| `agents/` | Agent framework stubs | v7.x-8.x |
| `ai_core/` | AI kernel stub | v8.x |
| `ai_runtime/` | AI runtime stubs | v8.x |
| `automation/` | Bash automation modules | v7.x |
| `autonomous/` | Autonomous runtime stubs | v8.x |
| `backups/` | Release archives (16MB Gold Master) | v8.x |
| `bundles_7x/` | v7.x bulk install bundles | v7.x |
| `cli/` | Legacy CLI wrapper | v7.x |
| `config/` | Legacy JSON/YAML configs | v7.x |
| `control_center/` | Termux control center | v7.x |
| `distributed/` | Distributed system stubs | v8.x |
| `hardening/` | Dependency/environment audit | v7.x |
| `installers/` | Android install history | v6.x |
| `intelligence/` | Repository intelligence reports | v7.x |
| `mission_engine/` | Mission execution stubs | v8.x |
| `plugins/` | Android plugin ecosystem | v8.x |
| `prompts/` | Legacy prompt templates | v7.x |
| `runtime/` | 411 generated JSON state files | v7.x-8.x |
| `sdk/` | Legacy SDK stubs | v7.x |
| `security/` | Security audit scripts | v7.x |
| `sessions/` | Legacy session state | v7.x |
| `studio/` | Studio dashboard stubs | v7.x |
| `templates/` | Module template | v7.x |
| `tools/` | Bash control center tools | v7.x |

## Policy

- Do not add new code here
- Do not import from these modules
- Active development belongs in `platform/`
- Knowledge base content belongs in `knowledge/`
