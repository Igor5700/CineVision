from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine(database_url: str, *, echo: bool = False) -> AsyncEngine:
    _ensure_sqlite_directory_exists(database_url)
    return create_async_engine(database_url, echo=echo)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


def _ensure_sqlite_directory_exists(database_url: str) -> None:
    if not database_url.startswith("sqlite"):
        return
    path = urlparse(database_url).path.lstrip("/")
    if not path or path == ":memory:":
        return
    Path(path).parent.mkdir(parents=True, exist_ok=True)
