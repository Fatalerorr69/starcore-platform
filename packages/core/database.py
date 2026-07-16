"""
Database
"""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from core.config import Settings, get_settings


class Base(DeclarativeBase):
    pass


def ensure_sqlite_directory(url: str) -> None:
    """Create the parent directory for a file-based SQLite URL, if needed.

    Handles both relative (sqlite:///path) and absolute
    (sqlite:////abs/path) SQLite URLs, as well as in-memory databases.
    """
    parsed = make_url(url)
    if not parsed.drivername.startswith("sqlite"):
        return
    database = parsed.database
    if not database or database == ":memory:":
        return
    Path(database).parent.mkdir(parents=True, exist_ok=True)


def create_engine_from_settings(settings: Settings) -> Engine:
    url = settings.database_url
    connect_args: dict = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        ensure_sqlite_directory(url)
    return create_engine(url, connect_args=connect_args)


def get_migration_head() -> str | None:
    """The latest Alembic revision declared by migrations/versions/.

    Reads only the migration scripts on disk (`alembic.ini`'s
    `script_location`) -- no database connection is opened.
    """
    cfg = Config("alembic.ini")
    script = ScriptDirectory.from_config(cfg)
    return script.get_current_head()


def get_database_revision(engine: Engine) -> str | None:
    """The Alembic revision a given database currently claims to be at.

    Returns None if the database has no `alembic_version` table at all --
    i.e. it has never been brought under Alembic's tracking (either it is
    genuinely brand new, or it predates this project adopting the
    create-then-stamp bootstrap in `init_db()`, see TD-17 / ADR-005).
    """
    with engine.connect() as conn:
        context = MigrationContext.configure(conn)
        return context.get_current_revision()


_engine: Engine | None = None
_session_factory: sessionmaker | None = None


def init_db(settings: Settings | None = None) -> Engine:
    global _engine, _session_factory

    if settings is None and _engine is not None:
        return _engine

    resolved_settings = settings or get_settings()
    _engine = create_engine_from_settings(resolved_settings)

    from . import models_db  # noqa: F401  (register ORM models with Base)

    _ensure_schema_at_head(_engine, resolved_settings.database_url)

    _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def _ensure_schema_at_head(engine: Engine, database_url: str) -> None:
    """Bring the database's schema under Alembic tracking, or fail fast.

    TD-17 / ADR-005: previously `Base.metadata.create_all()` ran
    unconditionally on every `init_db()` call, alongside a fully separate
    Alembic migration setup -- two schema-management mechanisms active at
    once, risking silent drift between ORM models and migration history.

    Exactly one of two things now happens:

    - The database has no `alembic_version` table yet (a genuinely fresh
      database, OR one created by this project's old always-`create_all()`
      behavior before this fix). `create_all()` runs exactly once more here
      (a no-op for any table that already exists) and the database is then
      stamped as being at the current Alembic head. This preserves today's
      "it just works" experience for a brand-new database (e.g. the
      README's Quick Start) while bringing it under Alembic's tracking
      from this point forward.
    - The database already has an `alembic_version` table. `create_all()`
      is never called again; if its recorded revision doesn't match the
      current head, startup fails immediately with an actionable error
      instead of running against a silently out-of-date schema.
    """
    head = get_migration_head()
    current = get_database_revision(engine)

    if current is None:
        Base.metadata.create_all(bind=engine)
        cfg = Config("alembic.ini")
        cfg.set_main_option("sqlalchemy.url", database_url)
        command.stamp(cfg, "head")
        return

    if current != head:
        raise RuntimeError(
            f"Database schema is at revision {current!r}, but STARCORE Platform "
            f"expects {head!r}. Run 'alembic upgrade head' before starting the "
            "application."
        )


def get_session() -> Session:
    if _session_factory is None:
        init_db()
    assert _session_factory is not None
    return _session_factory()
