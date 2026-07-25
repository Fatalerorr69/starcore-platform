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


async def test_run_logger_plugin_receives_run_completed_event():
    from core.events import event_bus

    from plugins import run_logger

    run_logger.completed_runs.clear()

    manager = PluginManager(plugins_dir="plugins")
    manager.load_all()

    await event_bus.emit(
        "run.completed",
        {"blueprint_name": "demo", "version": "1.0", "tasks": []},
    )

    assert len(run_logger.completed_runs) == 1
    assert run_logger.completed_runs[0]["blueprint_name"] == "demo"


async def test_load_all_twice_does_not_duplicate_event_subscriptions():
    from core.events import event_bus

    from plugins import run_logger

    run_logger.completed_runs.clear()

    manager = PluginManager(plugins_dir="plugins")
    manager.load_all()
    manager.load_all()

    await event_bus.emit(
        "run.completed",
        {"blueprint_name": "demo2", "version": "1.0", "tasks": []},
    )

    assert len(run_logger.completed_runs) == 1


def test_load_all_skips_plugin_with_broken_import(tmp_path):
    """Lines 56-58: ImportError during import_module is caught and the plugin is skipped."""
    plugin_dir = tmp_path / "bad_import_plugin"
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text("import _this_module_does_not_exist_xyz_starcore\n")

    manager = PluginManager(plugins_dir=str(tmp_path))
    loaded = manager.load_all()

    assert "bad_import_plugin" not in loaded


def test_load_all_skips_plugin_whose_register_raises(tmp_path):
    """Lines 67-69: Exception raised inside register() is caught and the plugin is skipped."""
    plugin_dir = tmp_path / "bad_register_plugin"
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text(
        "def register(context):\n    raise RuntimeError('simulated register failure')\n"
    )

    manager = PluginManager(plugins_dir=str(tmp_path))
    loaded = manager.load_all()

    assert "bad_register_plugin" not in loaded


def test_get_returns_loaded_plugin_or_none():
    """Line 80: get() returns the plugin module for a known name, None for an unknown one."""
    manager = PluginManager(plugins_dir="plugins")
    manager.load_all()

    assert manager.get("example_provider") is not None
    assert manager.get("does_not_exist") is None
