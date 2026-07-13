"""
Pytest fixtures
"""

from __future__ import annotations

import pytest
from core.config import Settings
from core.database import init_db


@pytest.fixture(autouse=True)
def _isolated_database(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(Settings(database_url=f"sqlite:///{db_path}"))
    yield
