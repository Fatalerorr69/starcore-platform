"""
AI Blueprint Generator

Uses the Anthropic API to translate a natural language description of
desired infrastructure into a STARCORE blueprint YAML document.
"""

from __future__ import annotations

import re

from anthropic import AsyncAnthropic
from anthropic.types import TextBlock
from core.config import get_settings

SYSTEM_PROMPT = """You generate STARCORE infrastructure blueprint YAML files.

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

_FENCE_RE = re.compile(r"^```(?:yaml|yml)?\s*|\s*```$", re.MULTILINE)


class BlueprintGenerationError(Exception):
    """Raised when a blueprint cannot be generated (e.g. missing API key)."""


def _strip_code_fences(text: str) -> str:
    return _FENCE_RE.sub("", text).strip()


async def generate_blueprint_yaml(description: str) -> str:
    """Generate a blueprint YAML string from a natural language description.

    Raises BlueprintGenerationError if the Anthropic API key is not
    configured or if the API call fails.
    """
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise BlueprintGenerationError(
            "AI blueprint generation is not configured. Set "
            "STARCORE_ANTHROPIC_API_KEY in .env (see .env.example)."
        )

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    try:
        response = await client.messages.create(
            model=settings.anthropic_model,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": description}],
        )
    except Exception as exc:
        raise BlueprintGenerationError(f"Anthropic API request failed: {exc}") from exc

    if not response.content:
        raise BlueprintGenerationError("Anthropic API returned an empty response.")

    first_block = response.content[0]
    if not isinstance(first_block, TextBlock):
        raise BlueprintGenerationError("Anthropic API returned a non-text response block.")

    return _strip_code_fences(first_block.text)
