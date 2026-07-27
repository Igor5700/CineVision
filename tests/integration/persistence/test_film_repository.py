from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from movielib.domain.entities.film import Film
from movielib.infrastructure.persistence.film_repository_sqlalchemy import SqlAlchemyFilmRepository


@pytest.fixture()
def repo(session_factory: async_sessionmaker[AsyncSession]) -> SqlAlchemyFilmRepository:
    return SqlAlchemyFilmRepository(session_factory)


def _film(film_id: int, title: str, **overrides: object) -> Film:
    defaults: dict[str, object] = {
        "kind": "movie",
        "year": 2020,
        "description": "d",
        "poster_url": None,
    }
    defaults.update(overrides)
    return Film(id=film_id, title=title, **defaults)  # type: ignore[arg-type]


async def test_upsert_many_then_get(repo: SqlAlchemyFilmRepository) -> None:
    await repo.upsert_many([_film(1, "Титаник", rating=7.9)])

    film = await repo.get(1)
    assert film is not None
    assert film.title == "Титаник"
    assert film.rating == 7.9


async def test_upsert_many_refreshes_an_existing_entry(repo: SqlAlchemyFilmRepository) -> None:
    await repo.upsert_many([_film(1, "Матрица", rating=8.0)])
    await repo.upsert_many([_film(1, "Матрица", rating=8.7), _film(2, "Матрица 2")])

    film = await repo.get(1)
    assert film is not None
    assert film.rating == 8.7
    assert await repo.get(2) is not None


async def test_search_by_title_is_case_and_substring_insensitive(
    repo: SqlAlchemyFilmRepository,
) -> None:
    await repo.upsert_many([_film(1, "Гарри Поттер и философский камень")])

    results = await repo.search_by_title("гарри поттер")

    assert len(results) == 1
    assert results[0].id == 1


async def test_search_by_title_respects_limit(repo: SqlAlchemyFilmRepository) -> None:
    await repo.upsert_many([_film(i, f"Фильм {i}") for i in range(1, 6)])

    results = await repo.search_by_title("фильм", limit=3)

    assert len(results) == 3
