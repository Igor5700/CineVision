from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from movielib.domain.entities.user import User
from movielib.domain.value_objects.balance import Balance
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.infrastructure.persistence.user_repository_sqlalchemy import SqlAlchemyUserRepository


@pytest.fixture()
def repo(session_factory: async_sessionmaker[AsyncSession]) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session_factory)


async def test_add_then_get_roundtrips(repo: SqlAlchemyUserRepository) -> None:
    user = User(
        telegram_id=TelegramId(42),
        username="ann",
        balance=Balance(10),
        registered_at=datetime.now(UTC),
        birthday=date(2000, 1, 1),
    )
    await repo.add(user)

    fetched = await repo.get(TelegramId(42))

    assert fetched is not None
    assert fetched.username == "ann"
    assert int(fetched.balance) == 10
    assert fetched.birthday == date(2000, 1, 1)


async def test_get_missing_user_returns_none(repo: SqlAlchemyUserRepository) -> None:
    assert await repo.get(TelegramId(999)) is None


async def test_save_updates_an_existing_user(repo: SqlAlchemyUserRepository) -> None:
    user = User(
        telegram_id=TelegramId(7),
        username="bob",
        balance=Balance(0),
        registered_at=datetime.now(UTC),
    )
    await repo.add(user)

    user.balance = Balance(500)
    user.birthday = date(1995, 6, 15)
    await repo.save(user)

    fetched = await repo.get(TelegramId(7))
    assert fetched is not None
    assert int(fetched.balance) == 500
    assert fetched.birthday == date(1995, 6, 15)
