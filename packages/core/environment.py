"""
Runtime Environment Detection

Identifies the kind of host STARCORE is currently executing on, so
diagnostics and audit output make deployment context explicit instead of
leaving operators to infer it from symptoms (e.g. disk paths or network
reachability differing between a Proxmox node and a cloud VPS).
"""

from __future__ import annotations

from pathlib import Path

_PROXMOX_VERSION_FILE = Path("/etc/pve/.version")
_DOCKERENV_FILE = Path("/.dockerenv")
_CGROUP_FILE = Path("/proc/1/cgroup")


def detect_runtime_environment() -> str:
    """Return the detected execution environment.

    One of:

    - ``"proxmox-host"`` -- running directly on a Proxmox VE node,
      detected via ``/etc/pve/.version``, which only exists while
      ``pve-cluster`` is running on that host.
    - ``"container"`` -- running inside a container (Docker or
      compatible), detected via ``/.dockerenv`` or a ``docker``/
      ``kubepods`` entry in ``/proc/1/cgroup``. This covers both a local
      Docker Compose deployment and a containerized cloud deployment --
      the two are indistinguishable from inside the container without
      probing cloud-provider metadata endpoints, which this
      homelab-focused tool does not attempt.
    - ``"local"`` -- neither of the above: a bare process on a developer
      workstation, or any other non-containerized, non-Proxmox host.
      Remote clients (a browser on desktop or mobile/Android hitting
      ``GET /ui``, a REST client calling the API with ``X-API-Key``) are
      a separate concern from server-side environment detection -- the
      API is already client-agnostic and requires no special handling
      per client type.

    This is a best-effort heuristic for operator-facing diagnostics, not
    a security boundary.
    """
    if _PROXMOX_VERSION_FILE.exists():
        return "proxmox-host"

    if _DOCKERENV_FILE.exists():
        return "container"

    try:
        cgroup_content = _CGROUP_FILE.read_text()
    except OSError:
        cgroup_content = ""
    if "docker" in cgroup_content or "kubepods" in cgroup_content:
        return "container"

    return "local"
