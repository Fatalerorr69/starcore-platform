from provider_sdk.base import BaseProvider


class DockerProvider(BaseProvider):
    name = "docker"

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> None:
        return None

    async def health(self) -> dict:
        return {
            "status": "ok",
            "provider": self.name,
        }

    async def list_resources(self) -> list:
        return []

    async def execute(self, task) -> None:
        print(f"[Docker] {task.action} {task.resource}")
