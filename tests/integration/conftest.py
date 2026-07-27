from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from movielib.infrastructure.persistence.engine import create_engine, create_session_factory

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture()
def sqlite_url(tmp_path: Path) -> Iterator[str]:
    db_path = tmp_path / "test.db"
    url = f"sqlite+aiosqlite:///{db_path.as_posix()}"
    previous_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = url
    try:
        config = Config(str(REPO_ROOT / "alembic.ini"))
        config.set_main_option("script_location", str(REPO_ROOT / "migrations"))
        command.upgrade(config, "head")
        yield url
    finally:
        if previous_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous_url


@pytest_asyncio.fixture()
async def session_factory(sqlite_url: str) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_engine(sqlite_url)
    try:
        yield create_session_factory(engine)
    finally:
        await engine.dispose()
