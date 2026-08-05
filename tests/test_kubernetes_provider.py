"""
Kubernetes Provider Tests
"""

from __future__ import annotations

import asyncio
import time
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from kubernetes.client.rest import ApiException
from orchestrator.task import Task
from providers.kubernetes.provider import KubernetesProvider

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_provider(connected: bool = True) -> KubernetesProvider:
    p = KubernetesProvider()
    if connected:
        p._api_client = MagicMock()  # type: ignore[assignment]
        p._apps_v1 = MagicMock()
        p._core_v1 = MagicMock()
    return p


def _task(action: str, resource: str, payload: dict[str, Any] | None = None) -> Task:
    return Task(
        id="t1",
        provider="kubernetes",
        action=action,
        resource=resource,
        payload=payload or {},
    )


def _api_exc(status: int) -> ApiException:
    exc = ApiException(status=status)
    exc.status = status
    return exc


# ---------------------------------------------------------------------------
# connect()
# ---------------------------------------------------------------------------


async def test_connect_succeeds_with_kubeconfig(monkeypatch):
    monkeypatch.setenv("STARCORE_KUBERNETES_KUBECONFIG", "/fake/kubeconfig")
    from core.config import get_settings

    get_settings.cache_clear()
    try:
        fake_api_client = MagicMock()
        with (
            patch("providers.kubernetes.provider.config.load_kube_config"),
            patch("providers.kubernetes.provider.client.ApiClient", return_value=fake_api_client),
            patch("providers.kubernetes.provider.client.VersionApi") as mock_version,
        ):
            mock_version.return_value.get_code.return_value = MagicMock(git_version="v1.30.0")
            p = KubernetesProvider()
            result = await p.connect()

        assert result is True
        assert p._api_client is fake_api_client
        assert p._apps_v1 is not None
        assert p._core_v1 is not None
    finally:
        get_settings.cache_clear()


async def test_connect_falls_back_to_incluster_then_kube_config():
    """When no kubeconfig env var set and in-cluster fails, falls back to load_kube_config."""
    from kubernetes.config import ConfigException

    fake_api_client = MagicMock()
    with (
        patch(
            "providers.kubernetes.provider.config.load_incluster_config",
            side_effect=ConfigException("not in cluster"),
        ),
        patch("providers.kubernetes.provider.config.load_kube_config"),
        patch("providers.kubernetes.provider.client.ApiClient", return_value=fake_api_client),
        patch("providers.kubernetes.provider.client.VersionApi") as mock_version,
    ):
        mock_version.return_value.get_code.return_value = MagicMock(git_version="v1.30.0")
        p = KubernetesProvider()
        result = await p.connect()

    assert result is True


async def test_connect_returns_false_when_version_probe_fails():
    with (
        patch("providers.kubernetes.provider.config.load_incluster_config"),
        patch("providers.kubernetes.provider.client.ApiClient"),
        patch("providers.kubernetes.provider.client.VersionApi") as mock_version,
    ):
        mock_version.return_value.get_code.side_effect = Exception("connection refused")
        p = KubernetesProvider()
        result = await p.connect()

    assert result is False
    assert p._api_client is None
    assert p._apps_v1 is None
    assert p._core_v1 is None


async def test_connect_already_connected_skips_reload():
    fake_client = MagicMock()
    p = KubernetesProvider()
    p._api_client = fake_client

    load_calls = []
    with patch(
        "providers.kubernetes.provider.config.load_kube_config",
        side_effect=lambda **_: load_calls.append(1),
    ):
        result = await p.connect()

    assert result is True
    assert load_calls == []
    assert p._api_client is fake_client


async def test_connect_is_safe_under_concurrent_calls():
    """Concurrent connect() calls must perform the version probe exactly once."""
    call_count = 0

    def _slow_load(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        time.sleep(0.05)
        return MagicMock(git_version="v1.30.0")

    fake_api_client = MagicMock()
    with (
        patch("providers.kubernetes.provider.config.load_incluster_config"),
        patch("providers.kubernetes.provider.client.ApiClient", return_value=fake_api_client),
        patch("providers.kubernetes.provider.client.VersionApi") as mock_version,
    ):
        mock_version.return_value.get_code.side_effect = _slow_load
        p = KubernetesProvider()
        results = await asyncio.gather(p.connect(), p.connect(), p.connect())

    assert results == [True, True, True]
    assert call_count == 1
    assert p._api_client is fake_api_client


# ---------------------------------------------------------------------------
# disconnect()
# ---------------------------------------------------------------------------


async def test_disconnect_clears_all_clients():
    p = _make_provider()
    await p.disconnect()
    assert p._api_client is None
    assert p._apps_v1 is None
    assert p._core_v1 is None


async def test_disconnect_idempotent_when_not_connected():
    p = KubernetesProvider()
    await p.disconnect()  # must not raise


# ---------------------------------------------------------------------------
# health()
# ---------------------------------------------------------------------------


async def test_health_disconnected():
    p = KubernetesProvider()
    result = await p.health()
    assert result["status"] == "disconnected"
    assert result["provider"] == "kubernetes"


async def test_health_ok():
    p = _make_provider()
    fake_version = MagicMock()
    fake_version.git_version = "v1.30.0"
    with patch("providers.kubernetes.provider.client.VersionApi") as mock_api:
        mock_api.return_value.get_code.return_value = fake_version
        result = await p.health()

    assert result["status"] == "ok"
    assert result["server_version"] == "v1.30.0"
    assert result["provider"] == "kubernetes"


async def test_health_error_when_version_probe_fails():
    p = _make_provider()
    with patch("providers.kubernetes.provider.client.VersionApi") as mock_api:
        mock_api.return_value.get_code.side_effect = Exception("unreachable")
        result = await p.health()

    assert result["status"] == "error"
    assert "unreachable" in result["detail"]


# ---------------------------------------------------------------------------
# list_resources()
# ---------------------------------------------------------------------------


async def test_list_resources_returns_empty_when_disconnected():
    p = KubernetesProvider()
    result = await p.list_resources()
    assert result == []


async def test_list_resources_returns_deployments():
    p = _make_provider()
    fake_d = MagicMock()
    fake_d.metadata.name = "web"
    fake_d.metadata.namespace = "production"
    fake_d.spec.replicas = 3
    fake_d.status.ready_replicas = 2
    p._apps_v1.list_deployment_for_all_namespaces.return_value = MagicMock(items=[fake_d])

    result = await p.list_resources()

    assert len(result) == 1
    assert result[0] == {
        "name": "web",
        "namespace": "production",
        "replicas": 3,
        "ready_replicas": 2,
        "kind": "deployment",
    }


async def test_list_resources_returns_empty_on_exception():
    p = _make_provider()
    p._apps_v1.list_deployment_for_all_namespaces.side_effect = Exception("api error")
    result = await p.list_resources()
    assert result == []


async def test_list_resources_handles_none_ready_replicas():
    p = _make_provider()
    fake_d = MagicMock()
    fake_d.metadata.name = "worker"
    fake_d.metadata.namespace = "default"
    fake_d.spec.replicas = 1
    fake_d.status.ready_replicas = None
    p._apps_v1.list_deployment_for_all_namespaces.return_value = MagicMock(items=[fake_d])

    result = await p.list_resources()
    assert result[0]["ready_replicas"] == 0


# ---------------------------------------------------------------------------
# execute() — dispatch guard
# ---------------------------------------------------------------------------


async def test_execute_raises_when_not_connected():
    p = KubernetesProvider()
    task = _task("deploy", "web", {"image": "nginx:latest"})
    with pytest.raises(RuntimeError, match="not connected"):
        await p.execute(task)


async def test_execute_raises_for_unsupported_action():
    p = _make_provider()
    task = _task("teleport", "web")
    with pytest.raises(ValueError, match="Unsupported Kubernetes action"):
        await p.execute(task)


# ---------------------------------------------------------------------------
# execute() — deploy
# ---------------------------------------------------------------------------


async def test_deploy_creates_new_deployment():
    p = _make_provider()
    p._apps_v1.read_namespaced_deployment.side_effect = _api_exc(404)

    task = _task("deploy", "web", {"image": "nginx:latest", "replicas": 2, "namespace": "prod"})
    await p.execute(task)

    p._apps_v1.create_namespaced_deployment.assert_called_once()
    p._apps_v1.patch_namespaced_deployment.assert_not_called()
    assert task.result == {"name": "web", "namespace": "prod", "replicas": 2}


async def test_deploy_updates_existing_deployment():
    p = _make_provider()
    p._apps_v1.read_namespaced_deployment.return_value = MagicMock()

    task = _task("deploy", "api", {"image": "myapp:v2", "namespace": "default"})
    await p.execute(task)

    p._apps_v1.patch_namespaced_deployment.assert_called_once()
    p._apps_v1.create_namespaced_deployment.assert_not_called()
    assert task.result["replicas"] == 1  # default


async def test_deploy_uses_default_namespace_from_settings(monkeypatch):
    monkeypatch.setenv("STARCORE_KUBERNETES_NAMESPACE", "staging")
    from core.config import get_settings

    get_settings.cache_clear()
    try:
        p = _make_provider()
        p._apps_v1.read_namespaced_deployment.side_effect = _api_exc(404)
        task = _task("deploy", "web", {"image": "nginx:latest"})
        await p.execute(task)
        assert task.result["namespace"] == "staging"
    finally:
        get_settings.cache_clear()


async def test_deploy_raises_without_image():
    p = _make_provider()
    task = _task("deploy", "web", {})
    with pytest.raises(ValueError, match="image"):
        await p.execute(task)


async def test_deploy_includes_env_vars():
    p = _make_provider()
    p._apps_v1.read_namespaced_deployment.side_effect = _api_exc(404)

    task = _task(
        "deploy",
        "worker",
        {"image": "worker:latest", "env": {"DB_HOST": "db.svc", "PORT": "5432"}},
    )
    await p.execute(task)

    create_call = p._apps_v1.create_namespaced_deployment.call_args
    body = create_call.kwargs["body"]
    containers = body.spec.template.spec.containers
    assert len(containers) == 1
    env_names = {e.name for e in containers[0].env}
    assert env_names == {"DB_HOST", "PORT"}


async def test_deploy_with_no_env_passes_none_to_container():
    p = _make_provider()
    p._apps_v1.read_namespaced_deployment.side_effect = _api_exc(404)

    task = _task("deploy", "web", {"image": "nginx:latest"})
    await p.execute(task)

    body = p._apps_v1.create_namespaced_deployment.call_args.kwargs["body"]
    assert body.spec.template.spec.containers[0].env is None


async def test_deploy_re_raises_non_404_api_exception():
    p = _make_provider()
    p._apps_v1.read_namespaced_deployment.side_effect = _api_exc(403)

    task = _task("deploy", "web", {"image": "nginx:latest"})
    with pytest.raises(ApiException) as exc_info:
        await p.execute(task)
    assert exc_info.value.status == 403


async def test_deploy_raises_when_not_connected():
    p = _make_provider()
    p._apps_v1 = None
    task = _task("deploy", "web", {"image": "nginx:latest"})
    with pytest.raises(RuntimeError, match="not connected"):
        p._apply_deployment(task, "default")


# ---------------------------------------------------------------------------
# execute() — delete
# ---------------------------------------------------------------------------


async def test_delete_calls_correct_endpoint():
    p = _make_provider()
    task = _task("delete", "web", {"namespace": "prod"})
    await p.execute(task)

    p._apps_v1.delete_namespaced_deployment.assert_called_once_with(
        name="web", namespace="prod"
    )
    assert task.result == {"name": "web", "namespace": "prod"}


async def test_delete_raises_when_not_connected():
    p = _make_provider()
    p._apps_v1 = None
    task = _task("delete", "web", {"namespace": "default"})
    with pytest.raises(RuntimeError, match="not connected"):
        p._delete_deployment(task, "default")


# ---------------------------------------------------------------------------
# execute() — scale
# ---------------------------------------------------------------------------


async def test_scale_patches_deployment_scale():
    p = _make_provider()
    task = _task("scale", "web", {"replicas": 5, "namespace": "default"})
    await p.execute(task)

    p._apps_v1.patch_namespaced_deployment_scale.assert_called_once_with(
        name="web", namespace="default", body={"spec": {"replicas": 5}}
    )
    assert task.result == {"name": "web", "namespace": "default", "replicas": 5}


async def test_scale_raises_without_replicas():
    p = _make_provider()
    task = _task("scale", "web", {"namespace": "default"})
    with pytest.raises(ValueError, match="replicas"):
        await p.execute(task)


async def test_scale_raises_when_not_connected():
    p = _make_provider()
    p._apps_v1 = None
    task = _task("scale", "web", {"replicas": 3})
    with pytest.raises(RuntimeError, match="not connected"):
        p._scale_deployment(task, "default")


# ---------------------------------------------------------------------------
# execute() — restart
# ---------------------------------------------------------------------------


async def test_restart_patches_deployment_annotation():
    p = _make_provider()
    task = _task("restart", "web", {"namespace": "default"})
    await p.execute(task)

    p._apps_v1.patch_namespaced_deployment.assert_called_once()
    patch_body = p._apps_v1.patch_namespaced_deployment.call_args.kwargs["body"]
    annotation = patch_body["spec"]["template"]["metadata"]["annotations"]
    assert "kubectl.kubernetes.io/restartedAt" in annotation
    assert task.result == {"name": "web", "namespace": "default"}


async def test_restart_raises_when_not_connected():
    p = _make_provider()
    p._apps_v1 = None
    task = _task("restart", "web")
    with pytest.raises(RuntimeError, match="not connected"):
        p._restart_deployment(task, "default")


# ---------------------------------------------------------------------------
# execute() — apply-namespace
# ---------------------------------------------------------------------------


async def test_apply_namespace_creates_when_missing():
    p = _make_provider()
    p._core_v1.read_namespace.side_effect = _api_exc(404)

    task = _task("apply-namespace", "monitoring")
    await p.execute(task)

    p._core_v1.create_namespace.assert_called_once()
    assert task.result == {"name": "monitoring"}


async def test_apply_namespace_is_idempotent_when_exists():
    p = _make_provider()
    p._core_v1.read_namespace.return_value = MagicMock()

    task = _task("apply-namespace", "production")
    await p.execute(task)

    p._core_v1.create_namespace.assert_not_called()
    assert task.result == {"name": "production"}


async def test_apply_namespace_re_raises_non_404_exception():
    p = _make_provider()
    p._core_v1.read_namespace.side_effect = _api_exc(403)

    task = _task("apply-namespace", "restricted")
    with pytest.raises(ApiException) as exc_info:
        await p.execute(task)
    assert exc_info.value.status == 403


async def test_apply_namespace_raises_when_not_connected():
    p = _make_provider()
    p._core_v1 = None
    task = _task("apply-namespace", "ns")
    with pytest.raises(RuntimeError, match="not connected"):
        p._apply_namespace(task)


# ---------------------------------------------------------------------------
# registry integration
# ---------------------------------------------------------------------------


def test_kubernetes_registered_in_default_providers():
    from provider_sdk.registry import ProviderRegistry

    test_registry = ProviderRegistry()

    from providers.docker.provider import DockerProvider
    from providers.kubernetes.provider import KubernetesProvider
    from providers.proxmox.provider import ProxmoxProvider

    for cls in (DockerProvider, ProxmoxProvider, KubernetesProvider):
        instance = cls()
        test_registry.register(instance)

    assert "kubernetes" in test_registry.names()
    assert isinstance(test_registry.get("kubernetes"), KubernetesProvider)


def test_register_default_providers_includes_kubernetes():
    from provider_sdk.registry import register_default_providers, registry

    backup = dict(registry._providers)
    registry._providers.clear()
    try:
        register_default_providers()
        assert "kubernetes" in registry.names()
    finally:
        registry._providers.clear()
        registry._providers.update(backup)
