"""
Database
"""

from __future__ import annotations

from pathlib import Path

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


_engine: Engine | None = None
_session_factory: sessionmaker | None = None


def init_db(settings: Settings | None = None) -> Engine:
    global _engine, _session_factory

    if settings is None and _engine is not None:
        return _engine

    _engine = create_engine_from_settings(settings or get_settings())

    from . import models_db  # noqa: F401  (register ORM models with Base)

    Base.metadata.create_all(bind=_engine)
    _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def get_session() -> Session:
    if _session_factory is None:
        init_db()
    assert _session_factory is not None
    return _session_factory()
