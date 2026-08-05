"""
TD-21 regression test: Settings() must never read a real .env file during
tests, even when one is physically present in the working directory (as
it is on a host where STARCORE has already been deployed).
"""

from __future__ import annotations

from core.config import Settings, get_settings


def test_settings_ignores_env_file_even_when_present(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "STARCORE_PROXMOX_HOST=production-host-that-must-not-leak\n"
        "STARCORE_API_KEY=production-key-that-must-not-leak\n"
    )
    get_settings.cache_clear()

    settings = Settings()

    assert settings.proxmox_host is None
    get_settings.cache_clear()
