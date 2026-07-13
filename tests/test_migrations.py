"""
Alembic Migration Tests
"""

from __future__ import annotations

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_head_creates_expected_tables(tmp_path):
    db_path = tmp_path / "migration_test.db"
    db_url = f"sqlite:///{db_path}"

    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    assert "blueprint_runs" in tables
    assert "task_runs" in tables
    assert "alembic_version" in tables


def test_alembic_downgrade_removes_tables(tmp_path):
    db_path = tmp_path / "migration_downgrade_test.db"
    db_url = f"sqlite:///{db_path}"

    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")

    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    assert "blueprint_runs" not in tables
    assert "task_runs" not in tables
