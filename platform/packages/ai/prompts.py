"""
Shared system prompt for all AI blueprint generators.
"""

from __future__ import annotations

BLUEPRINT_SYSTEM_PROMPT = """You generate STARCORE infrastructure blueprint YAML files.

Output ONLY valid YAML, nothing else: no markdown code fences, no
explanation, no commentary before or after.

The YAML schema is:

name: <short slug describing the blueprint>
version: "1.0"
resources:
  - name: <unique resource name>
    provider: docker | proxmox
    kind: container | vm | lxc
    config:
      # For provider: docker, kind: container
      #   image: <docker image, required>
      #   volume: <named volume, optional>
      #
      # For provider: proxmox, kind: vm or lxc
      #   node: <proxmox node name, required>
      #   template_vmid: <integer, required - VM/CT template to clone from>
      #   vmid: <integer, optional - auto-allocated if omitted>
      #   cores: <integer, optional>
      #   memory: <integer MB, optional>
      #   full: <bool, optional, default true - full vs linked clone>
      #   storage: <string, optional>
    depends_on:
      - <name of another resource in this same blueprint, optional>

Rules:
- Use depends_on when a resource logically needs another one to exist first
  (e.g. an app VM that depends on a database container).
- Prefer provider: docker for stateless services and databases unless the
  user explicitly asks for a VM or LXC container.
- Use realistic, common docker image tags (e.g. postgres:17, redis:7,
  nginx:latest) when the user does not specify one.
- If Proxmox resources are requested, use placeholder values for node
  (e.g. "changeme-node") and template_vmid (e.g. 9000) since the actual
  values depend on the user's environment.
- Keep resource names short, lowercase, hyphenated.
"""

_PROVIDER_HINT = (
    "\n\nAvailable infrastructure providers in this STARCORE instance: {providers}."
    " Only use providers from this list."
)


def build_system_prompt(
    available_providers: list[str] | None = None,
) -> str:
    """Build the system prompt, optionally scoping to available providers."""
    if not available_providers:
        return BLUEPRINT_SYSTEM_PROMPT
    joined = ", ".join(sorted(available_providers))
    return BLUEPRINT_SYSTEM_PROMPT + _PROVIDER_HINT.format(providers=joined)
