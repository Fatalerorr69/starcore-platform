"""
Tests for core.environment runtime detection.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import core.environment as environment
import httpx
import pytest
from core.environment import (
    classify_client_platform,
    detect_cloud_provider,
    detect_os_platform,
    detect_runtime_environment,
)


def test_detect_returns_proxmox_host_when_pve_version_file_exists(tmp_path, monkeypatch):
    pve_version = tmp_path / ".version"
    pve_version.write_text("8.2")
    monkeypatch.setattr(environment, "_PROXMOX_VERSION_FILE", pve_version)

    assert detect_runtime_environment() == "proxmox-host"


def test_detect_returns_container_when_dockerenv_file_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(environment, "_PROXMOX_VERSION_FILE", tmp_path / "no-pve-version")
    dockerenv = tmp_path / ".dockerenv"
    dockerenv.write_text("")
    monkeypatch.setattr(environment, "_DOCKERENV_FILE", dockerenv)

    assert detect_runtime_environment() == "container"


def test_detect_returns_container_when_cgroup_contains_docker(tmp_path, monkeypatch):
    monkeypatch.setattr(environment, "_PROXMOX_VERSION_FILE", tmp_path / "no-pve-version")
    monkeypatch.setattr(environment, "_DOCKERENV_FILE", tmp_path / "no-dockerenv")
    cgroup = tmp_path / "cgroup"
    cgroup.write_text("12:pids:/docker/abc123\n")
    monkeypatch.setattr(environment, "_CGROUP_FILE", cgroup)

    assert detect_runtime_environment() == "container"


def test_detect_returns_container_when_cgroup_contains_kubepods(tmp_path, monkeypatch):
    monkeypatch.setattr(environment, "_PROXMOX_VERSION_FILE", tmp_path / "no-pve-version")
    monkeypatch.setattr(environment, "_DOCKERENV_FILE", tmp_path / "no-dockerenv")
    cgroup = tmp_path / "cgroup"
    cgroup.write_text("12:pids:/kubepods/besteffort/pod123\n")
    monkeypatch.setattr(environment, "_CGROUP_FILE", cgroup)

    assert detect_runtime_environment() == "container"


def test_detect_returns_local_when_cgroup_file_unreadable(tmp_path, monkeypatch):
    monkeypatch.setattr(environment, "_PROXMOX_VERSION_FILE", tmp_path / "no-pve-version")
    monkeypatch.setattr(environment, "_DOCKERENV_FILE", tmp_path / "no-dockerenv")
    monkeypatch.setattr(environment, "_CGROUP_FILE", tmp_path / "no-cgroup-file")

    assert detect_runtime_environment() == "local"


def test_detect_returns_local_when_cgroup_content_matches_neither_marker(tmp_path, monkeypatch):
    monkeypatch.setattr(environment, "_PROXMOX_VERSION_FILE", tmp_path / "no-pve-version")
    monkeypatch.setattr(environment, "_DOCKERENV_FILE", tmp_path / "no-dockerenv")
    cgroup = tmp_path / "cgroup"
    cgroup.write_text("12:pids:/\n")
    monkeypatch.setattr(environment, "_CGROUP_FILE", cgroup)

    assert detect_runtime_environment() == "local"


def test_module_level_markers_are_path_instances():
    assert isinstance(environment._PROXMOX_VERSION_FILE, Path)
    assert isinstance(environment._DOCKERENV_FILE, Path)
    assert isinstance(environment._CGROUP_FILE, Path)


# ── detect_os_platform ──────────────────────────────────────────────────────


def test_detect_os_platform_non_linux_never_checks_wsl(monkeypatch):
    monkeypatch.setattr(environment.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(environment.platform, "release", lambda: "23.0")

    result = detect_os_platform()

    assert result == {"system": "Darwin", "release": "23.0", "is_wsl": False}


def test_detect_os_platform_linux_native_is_not_wsl(monkeypatch, tmp_path):
    monkeypatch.setattr(environment.platform, "system", lambda: "Linux")
    monkeypatch.setattr(environment.platform, "release", lambda: "6.1.0")
    proc_version = tmp_path / "version"
    proc_version.write_text("Linux version 6.1.0 (gcc)\n")
    monkeypatch.setattr(environment, "_PROC_VERSION_FILE", proc_version)

    result = detect_os_platform()

    assert result == {"system": "Linux", "release": "6.1.0", "is_wsl": False}


def test_detect_os_platform_linux_wsl_is_detected(monkeypatch, tmp_path):
    monkeypatch.setattr(environment.platform, "system", lambda: "Linux")
    monkeypatch.setattr(environment.platform, "release", lambda: "5.15.0-microsoft-standard")
    proc_version = tmp_path / "version"
    proc_version.write_text("Linux version 5.15.0 (Microsoft@Microsoft.com)\n")
    monkeypatch.setattr(environment, "_PROC_VERSION_FILE", proc_version)

    result = detect_os_platform()

    assert result["is_wsl"] is True


def test_detect_os_platform_linux_unreadable_proc_version_is_not_wsl(monkeypatch, tmp_path):
    monkeypatch.setattr(environment.platform, "system", lambda: "Linux")
    monkeypatch.setattr(environment.platform, "release", lambda: "6.1.0")
    monkeypatch.setattr(environment, "_PROC_VERSION_FILE", tmp_path / "does-not-exist")

    result = detect_os_platform()

    assert result["is_wsl"] is False


# ── detect_cloud_provider ────────────────────────────────────────────────────


def _mock_get_response(status_code: int) -> AsyncMock:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    return AsyncMock(return_value=resp)


async def test_detect_cloud_provider_returns_azure_on_200():
    mock_get = _mock_get_response(200)
    with patch("core.environment.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=MagicMock(get=mock_get))
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await detect_cloud_provider()

    assert result == "azure"


async def test_detect_cloud_provider_returns_aws_when_azure_unreachable():
    call_count = 0

    async def _side_effect(url: str, headers: dict) -> MagicMock:
        nonlocal call_count
        call_count += 1
        resp = MagicMock(spec=httpx.Response)
        if "169.254.169.254/latest/meta-data" in url:
            resp.status_code = 200
        else:
            raise httpx.ConnectTimeout("timed out")
        return resp

    with patch("core.environment.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(
            return_value=MagicMock(get=AsyncMock(side_effect=_side_effect))
        )
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await detect_cloud_provider()

    assert result == "aws"
    assert call_count == 2


async def test_detect_cloud_provider_returns_aws_on_401_imdsv2():
    async def _side_effect(url: str, headers: dict) -> MagicMock:
        resp = MagicMock(spec=httpx.Response)
        if "latest/meta-data" in url:
            resp.status_code = 401
        else:
            raise httpx.ConnectTimeout("timed out")
        return resp

    with patch("core.environment.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(
            return_value=MagicMock(get=AsyncMock(side_effect=_side_effect))
        )
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await detect_cloud_provider()

    assert result == "aws"


async def test_detect_cloud_provider_returns_gcp_when_others_unreachable():
    async def _side_effect(url: str, headers: dict) -> MagicMock:
        resp = MagicMock(spec=httpx.Response)
        if "metadata.google.internal" in url:
            resp.status_code = 200
        else:
            raise httpx.ConnectTimeout("timed out")
        return resp

    with patch("core.environment.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(
            return_value=MagicMock(get=AsyncMock(side_effect=_side_effect))
        )
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await detect_cloud_provider()

    assert result == "gcp"


async def test_detect_cloud_provider_returns_none_when_all_unreachable():
    mock_get = AsyncMock(side_effect=httpx.ConnectTimeout("timed out"))
    with patch("core.environment.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=MagicMock(get=mock_get))
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await detect_cloud_provider()

    assert result is None


async def test_detect_cloud_provider_returns_none_on_unexpected_status():
    mock_get = _mock_get_response(500)
    with patch("core.environment.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=MagicMock(get=mock_get))
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await detect_cloud_provider()

    assert result is None


# ── classify_client_platform ────────────────────────────────────────────────


@pytest.mark.parametrize("ua", [None, ""])
def test_classify_client_platform_missing_user_agent_is_unknown(ua):
    assert classify_client_platform(ua) == "unknown"


@pytest.mark.parametrize(
    "ua",
    [
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome Mobile",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
        "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X)",
    ],
)
def test_classify_client_platform_mobile_markers(ua):
    assert classify_client_platform(ua) == "browser-mobile"


@pytest.mark.parametrize(
    "ua",
    [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.0 Safari",
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    ],
)
def test_classify_client_platform_desktop_browser_markers(ua):
    assert classify_client_platform(ua) == "browser-desktop"


@pytest.mark.parametrize(
    "ua",
    [
        "curl/8.4.0",
        "python-httpx/0.28.1",
        "python-requests/2.31.0",
        "okhttp/4.12.0",
        "Go-http-client/1.1",
    ],
)
def test_classify_client_platform_script_markers(ua):
    assert classify_client_platform(ua) == "cli-or-script"


def test_classify_client_platform_unrecognized_is_unknown():
    assert classify_client_platform("SomeCustomAgent/1.0") == "unknown"
