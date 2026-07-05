"""
Proxmox Provider
"""

from provider_sdk.base import BaseProvider


class ProxmoxProvider(BaseProvider):

    name = "proxmox"

    async def connect(self):

        return True

    async def disconnect(self):

        return None

    async def health(self):

        return {
            "status": "ok"
        }

    async def list_resources(self):

        return []

    async def execute(self, task):

    print(
        f"[Proxmox] {task.action} {task.resource}"
    )
