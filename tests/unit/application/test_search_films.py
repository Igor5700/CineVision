from __future__ import annotations

from movielib.application.films.search_films import SearchFilms
from movielib.domain.entities.film import Film
from movielib.domain.value_objects.telegram_id import TelegramId
from tests.unit.fakes.fake_film_metadata_provider import FakeFilmMetadataProvider
from tests.unit.fakes.fake_film_repository import FakeFilmRepository
from tests.unit.fakes.fake_search_history_repository import FakeSearchHistoryRepository


def _film(film_id: int, title: str, **overrides: object) -> Film:
    defaults: dict[str, object] = {
        "kind": "movie",
        "year": 2020,
        "description": None,
        "poster_url": None,
    }
    defaults.update(overrides)
    return Film(id=film_id, title=title, **defaults)  # type: ignore[arg-type]


async def test_prefers_live_provider_results_over_the_cache() -> None:
    films = FakeFilmRepository()
    await films.upsert_many([_film(1, "Матрица (устаревшие данные)")])
    provider = FakeFilmMetadataProvider(results=[_film(1, "Матрица", rating=8.7)])
    search = SearchFilms(films, provider, FakeSearchHistoryRepository())

    results = await search("матрица")

    assert results[0].title == "Матрица"
    assert results[0].rating == 8.7


async def test_upserts_live_results_into_the_cache() -> None:
    films = FakeFilmRepository()
    provider = FakeFilmMetadataProvider(results=[_film(1, "Матрица")])
    search = SearchFilms(films, provider, FakeSearchHistoryRepository())

    await search("матрица")

    assert await films.get(1) is not None


async def test_falls_back_to_the_cache_when_the_provider_returns_nothing() -> None:
    films = FakeFilmRepository()
    await films.upsert_many([_film(1, "Матрица"), _film(2, "Матрица 2")])
    provider = FakeFilmMetadataProvider(results=[])
    search = SearchFilms(films, provider, FakeSearchHistoryRepository())

    results = await search("матрица")

    assert {film.id for film in results} == {1, 2}


async def test_respects_the_limit_on_live_results() -> None:
    films = FakeFilmRepository()
    provider = FakeFilmMetadataProvider(results=[_film(i, f"Фильм {i}") for i in range(1, 6)])
    search = SearchFilms(films, provider, FakeSearchHistoryRepository())

    results = await search("фильм", limit=2)

    assert len(results) == 2


async def test_logs_search_history_when_a_telegram_id_is_given() -> None:
    films = FakeFilmRepository()
    provider = FakeFilmMetadataProvider(results=[])
    search_history = FakeSearchHistoryRepository()
    search = SearchFilms(films, provider, search_history)

    await search("матрица", telegram_id=TelegramId(1))

    assert await search_history.list_recent(TelegramId(1)) == ["матрица"]


async def test_does_not_log_search_history_when_no_telegram_id_is_given() -> None:
    films = FakeFilmRepository()
    provider = FakeFilmMetadataProvider(results=[])
    search_history = FakeSearchHistoryRepository()
    search = SearchFilms(films, provider, search_history)

    await search("матрица")

    assert await search_history.list_recent(TelegramId(1)) == []
