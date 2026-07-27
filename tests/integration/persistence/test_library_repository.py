from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from movielib.domain.entities.film import Film
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.infrastructure.persistence.film_repository_sqlalchemy import SqlAlchemyFilmRepository
from movielib.infrastructure.persistence.library_repository_sqlalchemy import (
    SqlAlchemyLibraryRepository,
)

_USER = TelegramId(1)


@pytest.fixture()
def repo(session_factory: async_sessionmaker[AsyncSession]) -> SqlAlchemyLibraryRepository:
    return SqlAlchemyLibraryRepository(session_factory)


@pytest.fixture()
def films(session_factory: async_sessionmaker[AsyncSession]) -> SqlAlchemyFilmRepository:
    return SqlAlchemyFilmRepository(session_factory)


async def _seed_films(films: SqlAlchemyFilmRepository, *film_ids: int) -> None:
    await films.upsert_many(
        [
            Film(
                id=fid,
                title=f"Film {fid}",
                kind="movie",
                year=2020,
                description=None,
                poster_url=None,
            )
            for fid in film_ids
        ]
    )


async def test_watchlist_add_list_remove(
    repo: SqlAlchemyLibraryRepository, films: SqlAlchemyFilmRepository
) -> None:
    await _seed_films(films, 1)

    await repo.add_to_watchlist(_USER, 1)
    assert [f.id for f in await repo.list_watchlist(_USER)] == [1]

    await repo.remove_from_watchlist(_USER, 1)
    assert await repo.list_watchlist(_USER) == []


async def test_adding_to_watchlist_twice_is_idempotent(
    repo: SqlAlchemyLibraryRepository, films: SqlAlchemyFilmRepository
) -> None:
    await _seed_films(films, 1)

    await repo.add_to_watchlist(_USER, 1)
    await repo.add_to_watchlist(_USER, 1)

    assert [f.id for f in await repo.list_watchlist(_USER)] == [1]


async def test_removing_a_film_never_in_the_watchlist_is_a_no_op(
    repo: SqlAlchemyLibraryRepository,
) -> None:
    await repo.remove_from_watchlist(_USER, 999)


async def test_favorites_add_list_remove(
    repo: SqlAlchemyLibraryRepository, films: SqlAlchemyFilmRepository
) -> None:
    await _seed_films(films, 1)

    await repo.add_favorite(_USER, 1)
    assert [f.id for f in await repo.list_favorites(_USER)] == [1]

    await repo.remove_favorite(_USER, 1)
    assert await repo.list_favorites(_USER) == []


async def test_watchlist_and_favorites_are_independent(
    repo: SqlAlchemyLibraryRepository, films: SqlAlchemyFilmRepository
) -> None:
    await _seed_films(films, 1)

    await repo.add_to_watchlist(_USER, 1)

    assert await repo.list_favorites(_USER) == []


async def test_mark_watched_then_list_history_newest_first(
    repo: SqlAlchemyLibraryRepository, films: SqlAlchemyFilmRepository
) -> None:
    await _seed_films(films, 1, 2)

    await repo.mark_watched(_USER, 1)
    await repo.mark_watched(_USER, 2)

    assert [f.id for f in await repo.list_history(_USER)] == [2, 1]


async def test_list_history_respects_the_limit(
    repo: SqlAlchemyLibraryRepository, films: SqlAlchemyFilmRepository
) -> None:
    await _seed_films(films, 1, 2, 3)
    for film_id in (1, 2, 3):
        await repo.mark_watched(_USER, film_id)

    results = await repo.list_history(_USER, limit=2)

    assert len(results) == 2


async def test_relations_are_scoped_per_user(
    repo: SqlAlchemyLibraryRepository, films: SqlAlchemyFilmRepository
) -> None:
    await _seed_films(films, 1)
    await repo.add_to_watchlist(_USER, 1)

    assert await repo.list_watchlist(TelegramId(2)) == []
