"""
Kubernetes Provider
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

from core.config import get_settings
from core.security import scrub_configured_secrets
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from loguru import logger
from provider_sdk.base import BaseProvider


class KubernetesProvider(BaseProvider):
    """Infrastructure provider backed by a Kubernetes cluster.

    Authenticates via kubeconfig (``STARCORE_KUBERNETES_KUBECONFIG`` or
    ``~/.kube/config``) or in-cluster service account when the process runs
    inside a Pod. Exposes five actions against Deployments and Namespaces.

    A single :class:`KubernetesProvider` instance is shared via the global
    :class:`~provider_sdk.registry.ProviderRegistry`.  :meth:`connect` is
    safe to call concurrently — the underlying :class:`kubernetes.client.ApiClient`
    is created at most once per instance, guarded by
    :attr:`~provider_sdk.base.BaseProvider._connect_lock`.
    """

    name = "kubernetes"

    def __init__(self) -> None:
        self._api_client: client.ApiClient | None = None
        self._apps_v1: Any = None
        self._core_v1: Any = None

    async def connect(self) -> bool:
        async with self._connect_lock:
            if self._api_client is not None:
                return True
            try:
                settings = get_settings()
                api_client = await asyncio.to_thread(self._load_client, settings)
                self._api_client = api_client
                self._apps_v1 = client.AppsV1Api(api_client)
                self._core_v1 = client.CoreV1Api(api_client)
                return True
            except Exception as exc:
                logger.error(
                    "Kubernetes connection failed: {}", scrub_configured_secrets(str(exc))
                )
                self._api_client = None
                self._apps_v1 = None
                self._core_v1 = None
                return False

    @staticmethod
    def _load_client(settings) -> client.ApiClient:
        """Load kubeconfig and verify API server connectivity (blocking)."""
        if settings.kubernetes_kubeconfig:
            config.load_kube_config(
                config_file=settings.kubernetes_kubeconfig,
                context=settings.kubernetes_context or None,
            )
        else:
            try:
                config.load_incluster_config()
            except config.ConfigException:
                config.load_kube_config(context=settings.kubernetes_context or None)
        api_client = client.ApiClient()
        # Verify reachability with a lightweight version probe.
        client.VersionApi(api_client).get_code()
        return api_client

    async def disconnect(self) -> None:
        async with self._connect_lock:
            if self._api_client is not None:
                await asyncio.to_thread(self._api_client.rest_client.pool_manager.clear)
                self._api_client = None
                self._apps_v1 = None
                self._core_v1 = None

    async def health(self) -> dict[str, Any]:
        if self._api_client is None:
            return {"status": "disconnected", "provider": self.name}
        try:
            version: Any = await asyncio.to_thread(
                client.VersionApi(self._api_client).get_code
            )
            return {
                "status": "ok",
                "provider": self.name,
                "server_version": version.git_version,
            }
        except Exception as exc:
            return {
                "status": "error",
                "provider": self.name,
                "detail": scrub_configured_secrets(str(exc)),
            }

    async def list_resources(self) -> list[dict[str, Any]]:
        if self._api_client is None:
            return []
        try:
            deployments: Any = await asyncio.to_thread(
                self._apps_v1.list_deployment_for_all_namespaces
            )
            return [
                {
                    "name": d.metadata.name,
                    "namespace": d.metadata.namespace,
                    "replicas": d.spec.replicas,
                    "ready_replicas": d.status.ready_replicas or 0,
                    "kind": "deployment",
                }
                for d in deployments.items
            ]
        except Exception:
            return []

    async def execute(self, task) -> None:
        if self._api_client is None:
            raise RuntimeError("Kubernetes provider is not connected")

        settings = get_settings()
        namespace = task.payload.get("namespace", settings.kubernetes_namespace)
        action = task.action

        if action == "deploy":
            await asyncio.to_thread(self._apply_deployment, task, namespace)
        elif action == "delete":
            await asyncio.to_thread(self._delete_deployment, task, namespace)
        elif action == "scale":
            await asyncio.to_thread(self._scale_deployment, task, namespace)
        elif action == "restart":
            await asyncio.to_thread(self._restart_deployment, task, namespace)
        elif action == "apply-namespace":
            await asyncio.to_thread(self._apply_namespace, task)
        else:
            raise ValueError(f"Unsupported Kubernetes action: '{action}'")

    def _apply_deployment(self, task, namespace: str) -> None:
        if self._apps_v1 is None:
            raise RuntimeError("Kubernetes provider is not connected")
        image = task.payload.get("image")
        if not image:
            raise ValueError(f"Resource '{task.resource}' is missing required 'image' in config")

        replicas = int(task.payload.get("replicas", 1))
        env_vars = [
            client.V1EnvVar(name=k, value=str(v))
            for k, v in task.payload.get("env", {}).items()
        ]
        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(name=task.resource),
            spec=client.V1DeploymentSpec(
                replicas=replicas,
                selector=client.V1LabelSelector(match_labels={"app": task.resource}),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": task.resource}),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name=task.resource,
                                image=image,
                                env=env_vars or None,
                            )
                        ]
                    ),
                ),
            ),
        )
        try:
            self._apps_v1.read_namespaced_deployment(name=task.resource, namespace=namespace)
            self._apps_v1.patch_namespaced_deployment(
                name=task.resource, namespace=namespace, body=deployment
            )
            logger.info(
                "[Kubernetes] Updated deployment '{}' in namespace '{}'",
                task.resource,
                namespace,
            )
        except ApiException as exc:
            if exc.status == 404:
                self._apps_v1.create_namespaced_deployment(
                    namespace=namespace, body=deployment
                )
                logger.info(
                    "[Kubernetes] Created deployment '{}' in namespace '{}'",
                    task.resource,
                    namespace,
                )
            else:
                raise
        task.result = {"name": task.resource, "namespace": namespace, "replicas": replicas}

    def _delete_deployment(self, task, namespace: str) -> None:
        if self._apps_v1 is None:
            raise RuntimeError("Kubernetes provider is not connected")
        self._apps_v1.delete_namespaced_deployment(name=task.resource, namespace=namespace)
        logger.info(
            "[Kubernetes] Deleted deployment '{}' in namespace '{}'", task.resource, namespace
        )
        task.result = {"name": task.resource, "namespace": namespace}

    def _scale_deployment(self, task, namespace: str) -> None:
        if self._apps_v1 is None:
            raise RuntimeError("Kubernetes provider is not connected")
        replicas = task.payload.get("replicas")
        if replicas is None:
            raise ValueError(
                f"Resource '{task.resource}' is missing required 'replicas' in config"
            )
        replicas = int(replicas)
        self._apps_v1.patch_namespaced_deployment_scale(
            name=task.resource, namespace=namespace, body={"spec": {"replicas": replicas}}
        )
        logger.info(
            "[Kubernetes] Scaled deployment '{}' to {} replicas", task.resource, replicas
        )
        task.result = {"name": task.resource, "namespace": namespace, "replicas": replicas}

    def _restart_deployment(self, task, namespace: str) -> None:
        if self._apps_v1 is None:
            raise RuntimeError("Kubernetes provider is not connected")
        now = datetime.now(UTC).isoformat()
        self._apps_v1.patch_namespaced_deployment(
            name=task.resource,
            namespace=namespace,
            body={
                "spec": {
                    "template": {
                        "metadata": {
                            "annotations": {"kubectl.kubernetes.io/restartedAt": now}
                        }
                    }
                }
            },
        )
        logger.info(
            "[Kubernetes] Restarted deployment '{}' in namespace '{}'", task.resource, namespace
        )
        task.result = {"name": task.resource, "namespace": namespace}

    def _apply_namespace(self, task) -> None:
        if self._core_v1 is None:
            raise RuntimeError("Kubernetes provider is not connected")
        try:
            self._core_v1.read_namespace(name=task.resource)
            logger.info("[Kubernetes] Namespace '{}' already exists", task.resource)
        except ApiException as exc:
            if exc.status == 404:
                self._core_v1.create_namespace(
                    body=client.V1Namespace(
                        metadata=client.V1ObjectMeta(name=task.resource)
                    )
                )
                logger.info("[Kubernetes] Created namespace '{}'", task.resource)
            else:
                raise
        task.result = {"name": task.resource}
