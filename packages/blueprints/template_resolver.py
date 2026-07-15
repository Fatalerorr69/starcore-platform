"""
Template Resolver

Lets blueprints reference Proxmox templates by friendly name
(config: {template: "ubuntu-24.04"}) instead of a raw template_vmid.
Resolved using ProxmoxProvider.list_templates() (see core/discovery.py
for the underlying audit). Does nothing, and requires no Proxmox
connection, for blueprints that don't use the 'template' shorthand.
"""

from __future__ import annotations

from provider_sdk.registry import register_default_providers, registry

from .models import Blueprint


class TemplateResolutionError(Exception):
    """Raised when a 'template' alias cannot be resolved to a template_vmid."""


async def resolve_templates(blueprint: Blueprint) -> Blueprint:
    pending = [
        resource
        for resource in blueprint.resources
        if resource.provider == "proxmox"
        and "template" in resource.config
        and "template_vmid" not in resource.config
    ]
    if not pending:
        return blueprint

    register_default_providers()
    if "proxmox" not in registry.names():
        raise TemplateResolutionError(
            "Proxmox provider is not registered; cannot resolve template names"
        )

    provider = registry.get("proxmox")
    connected = await provider.connect()
    if not connected:
        raise TemplateResolutionError("Failed to connect to Proxmox to resolve template names")

    try:
        list_templates_fn = getattr(provider, "list_templates", None)
        templates = await list_templates_fn() if list_templates_fn else []
    finally:
        await provider.disconnect()

    for resource in pending:
        name = resource.config["template"]
        node_filter = resource.config.get("node")
        matches = [
            t
            for t in templates
            if t.get("name") == name and (node_filter is None or t["node"] == node_filter)
        ]
        if not matches:
            scope = f" on node '{node_filter}'" if node_filter else ""
            raise TemplateResolutionError(f"No template named '{name}' found{scope}")
        if len(matches) > 1:
            candidates = ", ".join(f"{m['node']}:{m['vmid']}" for m in matches)
            raise TemplateResolutionError(
                f"Template name '{name}' is ambiguous, found in multiple places: "
                f"{candidates}. Add 'node' to the resource config to disambiguate."
            )
        match = matches[0]
        resource.config["template_vmid"] = match["vmid"]
        resource.config.setdefault("node", match["node"])

    return blueprint
