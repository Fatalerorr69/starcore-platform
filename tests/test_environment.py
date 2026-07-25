"""
Tests for core.environment runtime detection.
"""

from __future__ import annotations

from pathlib import Path

import core.environment as environment
from core.environment import detect_runtime_environment


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
