from __future__ import annotations

import pytest

from movielib.application.films.get_film_details import GetFilmDetails
from movielib.domain.entities.film import Film
from movielib.domain.errors import FilmNotFoundError
from tests.unit.fakes.fake_film_metadata_provider import FakeFilmMetadataProvider
from tests.unit.fakes.fake_film_repository import FakeFilmRepository


async def test_returns_a_cached_film_without_calling_the_provider() -> None:
    films = FakeFilmRepository()
    await films.upsert_many(
        [Film(id=1, title="Матрица", kind="movie", year=1999, description="d", poster_url=None)]
    )
    provider = FakeFilmMetadataProvider()

    film = await GetFilmDetails(films, provider)(1)

    assert film.title == "Матрица"
    assert provider.queries == []


async def test_falls_back_to_a_live_lookup_and_caches_it() -> None:
    films = FakeFilmRepository()
    provider = FakeFilmMetadataProvider(
        results=[
            Film(id=1, title="Матрица", kind="movie", year=1999, description="d", poster_url=None)
        ]
    )

    film = await GetFilmDetails(films, provider)(1)

    assert film.title == "Матрица"
    assert await films.get(1) is not None


async def test_raises_when_missing_everywhere() -> None:
    films = FakeFilmRepository()
    provider = FakeFilmMetadataProvider()

    with pytest.raises(FilmNotFoundError):
        await GetFilmDetails(films, provider)(404)
