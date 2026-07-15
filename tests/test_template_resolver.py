"""
Template Resolver Tests
"""

from __future__ import annotations

import pytest
from blueprints.models import Blueprint, ResourceSpec
from blueprints.template_resolver import TemplateResolutionError, resolve_templates
from provider_sdk.base import BaseProvider
from provider_sdk.registry import registry


class FakeProxmoxProvider(BaseProvider):
    name = "proxmox"

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> None:
        return None

    async def health(self) -> dict:
        return {"status": "ok", "provider": self.name}

    async def list_resources(self) -> list[dict]:
        return []

    async def execute(self, task) -> None:
        return None

    async def list_templates(self) -> list[dict]:
        return [
            {"node": "fatalab", "vmid": 9000, "name": "ubuntu-24.04", "kind": "vm"},
            {"node": "fatalab2", "vmid": 9001, "name": "ubuntu-24.04", "kind": "vm"},
            {"node": "fatalab", "vmid": 8000, "name": "debian-12", "kind": "lxc"},
        ]


@pytest.fixture(autouse=True)
def clean_registry():
    registry._providers.clear()
    yield
    registry._providers.clear()


async def test_resolve_templates_skips_blueprints_without_template_shorthand():
    blueprint = Blueprint(
        name="demo",
        resources=[
            ResourceSpec(
                name="db", provider="docker", kind="container", config={"image": "postgres"}
            )
        ],
    )
    result = await resolve_templates(blueprint)
    assert result is blueprint


async def test_resolve_templates_fills_in_vmid_and_node():
    registry.register(FakeProxmoxProvider())
    blueprint = Blueprint(
        name="demo",
        resources=[
            ResourceSpec(
                name="web",
                provider="proxmox",
                kind="lxc",
                config={"template": "debian-12"},
            )
        ],
    )
    result = await resolve_templates(blueprint)
    assert result.resources[0].config["template_vmid"] == 8000
    assert result.resources[0].config["node"] == "fatalab"


async def test_resolve_templates_uses_node_to_disambiguate():
    registry.register(FakeProxmoxProvider())
    blueprint = Blueprint(
        name="demo",
        resources=[
            ResourceSpec(
                name="web",
                provider="proxmox",
                kind="vm",
                config={"template": "ubuntu-24.04", "node": "fatalab2"},
            )
        ],
    )
    result = await resolve_templates(blueprint)
    assert result.resources[0].config["template_vmid"] == 9001


async def test_resolve_templates_raises_on_ambiguous_match():
    registry.register(FakeProxmoxProvider())
    blueprint = Blueprint(
        name="demo",
        resources=[
            ResourceSpec(
                name="web",
                provider="proxmox",
                kind="vm",
                config={"template": "ubuntu-24.04"},
            )
        ],
    )
    with pytest.raises(TemplateResolutionError):
        await resolve_templates(blueprint)


async def test_resolve_templates_raises_on_no_match():
    registry.register(FakeProxmoxProvider())
    blueprint = Blueprint(
        name="demo",
        resources=[
            ResourceSpec(
                name="web",
                provider="proxmox",
                kind="vm",
                config={"template": "does-not-exist"},
            )
        ],
    )
    with pytest.raises(TemplateResolutionError):
        await resolve_templates(blueprint)


async def test_resolve_templates_raises_when_provider_not_registered():
    blueprint = Blueprint(
        name="demo",
        resources=[
            ResourceSpec(name="web", provider="proxmox", kind="vm", config={"template": "x"})
        ],
    )
    with pytest.raises(TemplateResolutionError):
        await resolve_templates(blueprint)
