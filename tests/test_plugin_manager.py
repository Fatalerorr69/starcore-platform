"""
Plugin Manager Tests
"""

from __future__ import annotations

import pytest
from core.plugin_manager import PluginManager
from provider_sdk.registry import registry


@pytest.fixture(autouse=True)
def clean_registry():
    registry._providers.clear()
    yield
    registry._providers.clear()


def test_discover_finds_example_plugin():
    manager = PluginManager(plugins_dir="plugins")
    discovered = manager.discover()
    assert "example_provider" in discovered


def test_discover_returns_empty_for_missing_directory(tmp_path):
    manager = PluginManager(plugins_dir=str(tmp_path / "does-not-exist"))
    assert manager.discover() == []


def test_discover_ignores_directories_without_init(tmp_path):
    (tmp_path / "not_a_plugin").mkdir()
    manager = PluginManager(plugins_dir=str(tmp_path))
    assert manager.discover() == []


def test_load_all_registers_noop_provider_from_example_plugin():
    manager = PluginManager(plugins_dir="plugins")
    loaded = manager.load_all()

    assert "example_provider" in loaded
    assert "noop" in registry.names()
    assert "example_provider" in manager.names()


def test_load_all_skips_plugin_without_register_function(tmp_path):
    broken = tmp_path / "broken_plugin"
    broken.mkdir()
    (broken / "__init__.py").write_text("# no register() here\n")

    manager = PluginManager(plugins_dir=str(tmp_path))
    loaded = manager.load_all()

    assert loaded == []
