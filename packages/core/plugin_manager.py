"""
Plugin Manager
"""

from pathlib import Path


class PluginManager:

    def __init__(self):
        self.plugins = {}

    def discover(self):

        plugin_dir = Path("plugins")

        if not plugin_dir.exists():
            return

        for plugin in plugin_dir.iterdir():

            if plugin.is_dir():
                self.plugins[plugin.name] = plugin

    def list(self):
        return sorted(self.plugins.keys())
