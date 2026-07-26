"""
Property-Based Tests — Environment Detection

Verifies structural invariants for core.environment's pure/deterministic
functions that must hold for all valid inputs.
"""

from __future__ import annotations

import core.environment as environment
from core.environment import classify_client_platform, detect_os_platform
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

_VALID_CLIENT_PLATFORMS = {"browser-mobile", "browser-desktop", "cli-or-script", "unknown"}

# ── classify_client_platform ────────────────────────────────────────────────


@given(user_agent=st.one_of(st.none(), st.text(max_size=200)))
def test_classify_client_platform_never_raises_and_returns_known_bucket(
    user_agent: str | None,
) -> None:
    """classify_client_platform() never raises and always returns one of the four buckets."""
    result = classify_client_platform(user_agent)
    assert result in _VALID_CLIENT_PLATFORMS


@given(user_agent=st.text(max_size=200))
def test_classify_client_platform_is_case_insensitive(user_agent: str) -> None:
    """Classification is stable regardless of the input's letter casing."""
    assert classify_client_platform(user_agent) == classify_client_platform(user_agent.upper())
    assert classify_client_platform(user_agent) == classify_client_platform(user_agent.lower())


@given(
    prefix=st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", max_size=30),
    marker=st.sampled_from(["android", "iphone", "ipad", "mobile"]),
    suffix=st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", max_size=30),
)
def test_classify_client_platform_any_string_containing_mobile_marker_is_mobile(
    prefix: str, marker: str, suffix: str
) -> None:
    """Any User-Agent containing a mobile marker classifies as browser-mobile."""
    ua = f"{prefix}{marker}{suffix}"
    assert classify_client_platform(ua) == "browser-mobile"


@given(
    prefix=st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", max_size=30),
    marker=st.sampled_from(["curl", "python-httpx", "python-requests", "okhttp"]),
    suffix=st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", max_size=30),
)
def test_classify_client_platform_any_string_containing_script_marker_is_script(
    prefix: str, marker: str, suffix: str
) -> None:
    """Any User-Agent with a script marker (and no mobile marker) classifies as cli-or-script."""
    ua = f"{prefix}{marker}{suffix}"
    mobile_markers = ("android", "iphone", "ipad", "mobile")
    if any(m in ua.lower() for m in mobile_markers):
        return
    assert classify_client_platform(ua) == "cli-or-script"


# ── detect_os_platform ──────────────────────────────────────────────────────


@given(
    system=st.sampled_from(["Linux", "Darwin", "Windows"]),
    proc_version=st.text(max_size=100),
    inject_microsoft=st.booleans(),
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_detect_os_platform_is_wsl_matches_proc_version_content(
    tmp_path, monkeypatch, system: str, proc_version: str, inject_microsoft: bool
) -> None:
    """is_wsl is True iff system is Linux and /proc/version contains 'microsoft'."""
    content = f"{proc_version} microsoft" if inject_microsoft else proc_version
    version_file = tmp_path / "version"
    version_file.write_text(content)

    monkeypatch.setattr(environment.platform, "system", lambda: system)
    monkeypatch.setattr(environment.platform, "release", lambda: "1.0")
    monkeypatch.setattr(environment, "_PROC_VERSION_FILE", version_file)

    result = detect_os_platform()

    expected_wsl = system == "Linux" and "microsoft" in content.lower()
    assert result["is_wsl"] == expected_wsl
    assert result["system"] == system


@given(system=st.sampled_from(["Linux", "Darwin", "Windows"]), release=st.text(max_size=50))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_detect_os_platform_always_returns_expected_keys(
    monkeypatch, system: str, release: str
) -> None:
    """The returned dict always has exactly the system/release/is_wsl keys."""
    monkeypatch.setattr(environment.platform, "system", lambda: system)
    monkeypatch.setattr(environment.platform, "release", lambda: release)

    result = detect_os_platform()

    assert set(result.keys()) == {"system", "release", "is_wsl"}
    assert result["system"] == system
    assert result["release"] == release
    assert isinstance(result["is_wsl"], bool)
