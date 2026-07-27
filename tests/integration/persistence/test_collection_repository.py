from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from movielib.domain.entities.collection import Collection
from movielib.domain.entities.film import Film
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.infrastructure.persistence.collection_repository_sqlalchemy import (
    SqlAlchemyCollectionRepository,
)
from movielib.infrastructure.persistence.film_repository_sqlalchemy import SqlAlchemyFilmRepository

_USER = TelegramId(1)
_FILM_ID = 101


@pytest.fixture()
def repo(session_factory: async_sessionmaker[AsyncSession]) -> SqlAlchemyCollectionRepository:
    return SqlAlchemyCollectionRepository(session_factory)


@pytest.fixture()
def films(session_factory: async_sessionmaker[AsyncSession]) -> SqlAlchemyFilmRepository:
    return SqlAlchemyFilmRepository(session_factory)


async def test_create_assigns_an_id(repo: SqlAlchemyCollectionRepository) -> None:
    created = await repo.create(
        Collection(
            id=None, telegram_id=_USER, name="Мои", description=None, created_at=datetime.now(UTC)
        )
    )

    assert created.id is not None
    fetched = await repo.get(created.id)
    assert fetched is not None
    assert fetched.name == "Мои"


async def test_list_for_user(repo: SqlAlchemyCollectionRepository) -> None:
    await repo.create(
        Collection(
            id=None, telegram_id=_USER, name="Мои", description=None, created_at=datetime.now(UTC)
        )
    )
    await repo.create(
        Collection(
            id=None,
            telegram_id=TelegramId(2),
            name="Чужие",
            description=None,
            created_at=datetime.now(UTC),
        )
    )

    mine = await repo.list_for_user(_USER)

    assert [c.name for c in mine] == ["Мои"]


async def test_delete_removes_the_collection(repo: SqlAlchemyCollectionRepository) -> None:
    created = await repo.create(
        Collection(
            id=None, telegram_id=_USER, name="Мои", description=None, created_at=datetime.now(UTC)
        )
    )
    assert created.id is not None

    await repo.delete(created.id)

    assert await repo.get(created.id) is None


async def test_add_list_remove_films(
    repo: SqlAlchemyCollectionRepository, films: SqlAlchemyFilmRepository
) -> None:
    await films.upsert_many(
        [
            Film(
                id=_FILM_ID,
                title="Матрица",
                kind="movie",
                year=1999,
                description=None,
                poster_url=None,
            )
        ]
    )
    created = await repo.create(
        Collection(
            id=None, telegram_id=_USER, name="Мои", description=None, created_at=datetime.now(UTC)
        )
    )
    assert created.id is not None

    await repo.add_film(created.id, _FILM_ID)
    assert [f.id for f in await repo.list_films(created.id)] == [_FILM_ID]

    await repo.remove_film(created.id, _FILM_ID)
    assert await repo.list_films(created.id) == []


async def test_adding_a_film_twice_is_idempotent(
    repo: SqlAlchemyCollectionRepository, films: SqlAlchemyFilmRepository
) -> None:
    await films.upsert_many(
        [
            Film(
                id=_FILM_ID,
                title="Матрица",
                kind="movie",
                year=1999,
                description=None,
                poster_url=None,
            )
        ]
    )
    created = await repo.create(
        Collection(
            id=None, telegram_id=_USER, name="Мои", description=None, created_at=datetime.now(UTC)
        )
    )
    assert created.id is not None

    await repo.add_film(created.id, _FILM_ID)
    await repo.add_film(created.id, _FILM_ID)

    assert [f.id for f in await repo.list_films(created.id)] == [_FILM_ID]
