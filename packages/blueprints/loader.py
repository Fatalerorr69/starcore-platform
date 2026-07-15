"""
Blueprint Loader
"""

from pathlib import Path

import yaml

from .models import Blueprint


class BlueprintLoader:
    @staticmethod
    def load(path: str | Path) -> Blueprint:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return Blueprint.model_validate(data)

    @staticmethod
    def load_from_string(text: str) -> Blueprint:
        data = yaml.safe_load(text)
        return Blueprint.model_validate(data)
