from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.infrastructure.persistence.search_history_repository_sqlalchemy import (
    SqlAlchemySearchHistoryRepository,
)

_USER = TelegramId(1)


@pytest.fixture()
def repo(session_factory: async_sessionmaker[AsyncSession]) -> SqlAlchemySearchHistoryRepository:
    return SqlAlchemySearchHistoryRepository(session_factory)


async def test_log_then_list_recent_newest_first(repo: SqlAlchemySearchHistoryRepository) -> None:
    await repo.log(_USER, "матрица")
    await repo.log(_USER, "начало")

    assert await repo.list_recent(_USER) == ["начало", "матрица"]


async def test_repeating_a_query_bumps_it_to_the_top(
    repo: SqlAlchemySearchHistoryRepository,
) -> None:
    await repo.log(_USER, "матрица")
    await repo.log(_USER, "начало")
    await repo.log(_USER, "матрица")

    assert await repo.list_recent(_USER) == ["матрица", "начало"]


async def test_respects_the_limit(repo: SqlAlchemySearchHistoryRepository) -> None:
    await repo.log(_USER, "a")
    await repo.log(_USER, "b")
    await repo.log(_USER, "c")

    assert len(await repo.list_recent(_USER, limit=2)) == 2


async def test_scoped_per_user(repo: SqlAlchemySearchHistoryRepository) -> None:
    await repo.log(_USER, "матрица")

    assert await repo.list_recent(TelegramId(2)) == []
