"""
Schema Management Tests

TD-17 / RISK-09 / ADR-005 regression tests: init_db() previously called
Base.metadata.create_all() unconditionally on every call, alongside a
fully separate Alembic migration setup, risking silent drift between ORM
models and migration history. See docs/changelog/sprint-004.md.
"""

from __future__ import annotations

import pytest
from alembic import command
from alembic.config import Config
from core.config import Settings
from core.database import (
    Base,
    create_engine_from_settings,
    get_database_revision,
    get_migration_head,
    init_db,
)
from sqlalchemy import create_engine, inspect, text


def test_fresh_database_is_created_and_stamped_to_head(tmp_path):
    """A genuinely new database (no alembic_version table) must still get
    a working schema (today's "it just works" Quick Start experience) --
    but must come out of init_db() tracked by Alembic, not left implicitly
    managed by create_all() alone.
    """
    db_path = tmp_path / "fresh.db"
    settings = Settings(database_url=f"sqlite:///{db_path}")

    engine = init_db(settings)

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    assert "blueprint_runs" in tables
    assert "task_runs" in tables
    assert "alembic_version" in tables

    assert get_database_revision(engine) == get_migration_head()


def test_legacy_create_all_only_database_is_safely_adopted(tmp_path):
    """A database created by the OLD (pre-ADR-005) always-create_all()
    behavior -- tables exist, but no alembic_version table, and it may
    already contain real data -- must be adopted (stamped to head) without
    data loss and without error on the next init_db() call.
    """
    db_path = tmp_path / "legacy.db"
    db_url = f"sqlite:///{db_path}"
    settings = Settings(database_url=db_url)

    # Simulate the old behavior: create tables via ORM metadata only,
    # completely bypassing Alembic, and insert a row -- exactly what an
    # existing pre-ADR-005 deployment's database looks like.
    legacy_engine = create_engine_from_settings(settings)
    from core import models_db  # noqa: F401  (register ORM models with Base)

    Base.metadata.create_all(bind=legacy_engine)
    with legacy_engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO blueprint_runs (id, blueprint_name, version, "
                "parallel, created_at) VALUES ('r1', 'legacy-bp', '1.0', 0, "
                "'2026-01-01T00:00:00')"
            )
        )
    legacy_engine.dispose()

    inspector = inspect(create_engine(db_url))
    assert "alembic_version" not in set(inspector.get_table_names())

    # Now go through the real init_db() path, as the application would on
    # its next startup.
    engine = init_db(settings)

    assert get_database_revision(engine) == get_migration_head()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT blueprint_name FROM blueprint_runs WHERE id = 'r1'")
        ).fetchone()
    assert row is not None
    assert row[0] == "legacy-bp"


def test_database_already_at_head_is_left_untouched(tmp_path):
    """A database that already went through `alembic upgrade head`
    (the Docker deployment path) must be accepted as-is, with no
    create_all() call and no error.
    """
    db_path = tmp_path / "at_head.db"
    db_url = f"sqlite:///{db_path}"
    settings = Settings(database_url=db_url)

    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(cfg, "head")

    engine = init_db(settings)

    assert get_database_revision(engine) == get_migration_head()
    inspector = inspect(engine)
    assert "blueprint_runs" in set(inspector.get_table_names())


def test_stale_database_revision_fails_fast_instead_of_drifting(tmp_path):
    """A database whose recorded Alembic revision does not match the
    current head must refuse to start with an actionable error, instead
    of silently running against a potentially-incomplete schema the way
    the old unconditional create_all() would have.
    """
    db_path = tmp_path / "stale.db"
    db_url = f"sqlite:///{db_path}"
    settings = Settings(database_url=db_url)

    # Craft a database with a stale alembic_version row (simulating a
    # database that hasn't had a newer migration applied yet).
    engine = create_engine_from_settings(settings)
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32))"))
        conn.execute(text("INSERT INTO alembic_version VALUES ('0000_stale_revision')"))
    engine.dispose()

    with pytest.raises(RuntimeError, match="alembic upgrade head"):
        init_db(settings)
