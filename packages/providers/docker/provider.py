"""
Docker Provider
"""

from __future__ import annotations

import asyncio
from typing import Any

import docker
from docker.errors import DockerException, NotFound
from loguru import logger
from provider_sdk.base import BaseProvider


class DockerProvider(BaseProvider):
    name = "docker"

    def __init__(self) -> None:
        self._client: docker.DockerClient | None = None

    async def connect(self) -> bool:
        try:
            self._client = await asyncio.to_thread(docker.from_env)
            await asyncio.to_thread(self._client.ping)
            return True
        except DockerException as exc:
            logger.error("Docker connection failed: {}", exc)
            self._client = None
            return False

    async def disconnect(self) -> None:
        if self._client is not None:
            await asyncio.to_thread(self._client.close)
            self._client = None

    async def health(self) -> dict[str, Any]:
        if self._client is None:
            return {"status": "disconnected", "provider": self.name}
        try:
            await asyncio.to_thread(self._client.ping)
            return {"status": "ok", "provider": self.name}
        except DockerException as exc:
            return {"status": "error", "provider": self.name, "detail": str(exc)}

    async def list_resources(self) -> list[dict]:
        if self._client is None:
            return []
        containers = await asyncio.to_thread(self._client.containers.list, all=True)
        resources = []
        for container in containers:
            image = container.image
            tag = image.tags[0] if image is not None and image.tags else None
            resources.append(
                {
                    "id": container.id,
                    "name": container.name,
                    "status": container.status,
                    "image": tag or (image.id if image is not None else None),
                }
            )
        return resources

    async def execute(self, task) -> None:
        if self._client is None:
            raise RuntimeError("Docker provider is not connected")

        action = task.action
        if action == "create":
            await asyncio.to_thread(self._ensure_container, task)
        elif action in ("start", "stop"):
            await asyncio.to_thread(self._container_action, task.resource, action)
        elif action == "remove":
            await asyncio.to_thread(self._container_action, task.resource, "remove", force=True)
        else:
            raise ValueError(f"Unsupported Docker action: '{action}'")

    def _ensure_container(self, task) -> None:
        assert self._client is not None
        try:
            self._client.containers.get(task.resource)
            logger.info("[Docker] Container '{}' already exists", task.resource)
            return
        except NotFound:
            pass

        image = task.payload.get("image")
        if not image:
            raise ValueError(f"Resource '{task.resource}' is missing required 'image' in config")

        volume = task.payload.get("volume")
        volumes = {volume: {"bind": f"/data/{volume}", "mode": "rw"}} if volume else None

        self._client.containers.run(
            image,
            name=task.resource,
            volumes=volumes,
            detach=True,
        )
        logger.info("[Docker] Created container '{}' from image '{}'", task.resource, image)

    def _container_action(self, name: str, action: str, **kwargs: Any) -> None:
        assert self._client is not None
        container = self._client.containers.get(name)
        getattr(container, action)(**kwargs)
        logger.info("[Docker] {} -> {}", action, name)
