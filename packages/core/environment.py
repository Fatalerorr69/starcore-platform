"""
Runtime Environment Detection

Identifies the kind of host STARCORE is currently executing on, so
diagnostics and audit output make deployment context explicit instead of
leaving operators to infer it from symptoms (e.g. disk paths or network
reachability differing between a Proxmox node and a cloud VPS).

Three independent, composable checks live here:

- ``detect_runtime_environment()`` -- fast, local-only: proxmox-host /
  container / local. Safe to call from any command, including ones that
  are documented as instant (``starcore audit``, ``starcore doctor``).
- ``detect_os_platform()`` -- fast, local-only: OS family, release, and
  whether it's WSL (relevant to the "local" bucket -- a Windows dev
  machine running STARCORE under WSL behaves differently for filesystem
  and networking purposes than native Linux).
- ``detect_cloud_provider()`` -- bounded-timeout network probe against
  well-known cloud metadata endpoints (AWS/GCP/Azure). Only meaningful
  to distinguish "cloud VPS" from "local machine" within the "container"
  or "local" buckets; deliberately NOT called from the fast/local-only
  commands -- only from `run_diagnostics()`, which already makes
  provider network calls and is documented as a deep, non-instant check.
- ``classify_client_platform()`` -- pure string classification of a
  request's User-Agent header, for reporting which *kind* of client
  (desktop browser, mobile browser/Android, CLI/script) is calling the
  API right now. This is a per-request concern, not a server property.
"""

from __future__ import annotations

import platform
from pathlib import Path

import httpx

_PROXMOX_VERSION_FILE = Path("/etc/pve/.version")
_DOCKERENV_FILE = Path("/.dockerenv")
_CGROUP_FILE = Path("/proc/1/cgroup")
_PROC_VERSION_FILE = Path("/proc/version")

_CLOUD_METADATA_TIMEOUT = 0.25


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


def detect_os_platform() -> dict[str, object]:
    """Return local OS details: family, release, and WSL status.

    ``is_wsl`` is relevant only on Linux: WSL (Windows Subsystem for
    Linux) reports ``platform.system() == "Linux"`` like any native
    Linux host, but its kernel version string identifies it, and it has
    real behavioral differences (filesystem performance across the
    Windows/Linux boundary, networking) that matter for a workstation
    running STARCORE locally.
    """
    system = platform.system()
    is_wsl = False
    if system == "Linux":
        try:
            version_content = _PROC_VERSION_FILE.read_text().lower()
        except OSError:
            version_content = ""
        is_wsl = "microsoft" in version_content

    return {
        "system": system,
        "release": platform.release(),
        "is_wsl": is_wsl,
    }


async def detect_cloud_provider(timeout: float = _CLOUD_METADATA_TIMEOUT) -> str | None:
    """Best-effort identification of the cloud provider hosting this process.

    Probes well-known link-local cloud metadata endpoints with a short
    timeout each. On a homelab machine or a Proxmox node these addresses
    are normally unreachable, so every probe fails fast and this returns
    ``None`` quickly rather than hanging. Never raises -- a network error,
    timeout, or unexpected response is treated the same as "not this
    provider".

    Returns one of ``"azure"``, ``"aws"``, ``"gcp"``, or ``None``.
    """
    probes: list[tuple[str, str, dict[str, str]]] = [
        (
            "azure",
            "http://169.254.169.254/metadata/instance?api-version=2021-02-01",
            {"Metadata": "true"},
        ),
        ("aws", "http://169.254.169.254/latest/meta-data/", {}),
        (
            "gcp",
            "http://metadata.google.internal/computeMetadata/v1/",
            {"Metadata-Flavor": "Google"},
        ),
    ]

    for provider_name, url, headers in probes:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, headers=headers)
            if response.status_code in (200, 401):
                return provider_name
        except httpx.HTTPError:
            continue

    return None


def classify_client_platform(user_agent: str | None) -> str:
    """Classify an HTTP client's User-Agent header into a broad platform bucket.

    Returns one of ``"browser-mobile"``, ``"browser-desktop"``,
    ``"cli-or-script"``, or ``"unknown"``. This is a coarse, best-effort
    heuristic for operator-facing diagnostics (e.g. "this request to
    /diagnostics came from a mobile browser") -- not a security or
    access-control mechanism.
    """
    if not user_agent:
        return "unknown"

    ua = user_agent.lower()

    mobile_markers = ("android", "iphone", "ipad", "mobile")
    if any(marker in ua for marker in mobile_markers):
        return "browser-mobile"

    browser_markers = ("mozilla", "chrome", "safari", "firefox", "edge")
    if any(marker in ua for marker in browser_markers):
        return "browser-desktop"

    script_markers = ("curl", "python-httpx", "python-requests", "okhttp", "go-http-client")
    if any(marker in ua for marker in script_markers):
        return "cli-or-script"

    return "unknown"
