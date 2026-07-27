from __future__ import annotations

import re

from aioresponses import aioresponses
from fastapi.testclient import TestClient

from movielib.bootstrap.container import Container
from movielib.domain.entities.film import Film
from movielib.infrastructure.persistence.film_repository_sqlalchemy import (
    SqlAlchemyFilmRepository,
)

_SEARCH_URL_PATTERN = re.compile(r"^https://api\.kinopoisk\.dev/v1\.4/movie/search.*")
_DETAILS_URL_PATTERN = re.compile(r"^https://api\.kinopoisk\.dev/v1\.4/movie/\d+$")


async def _seed(container: Container, film: Film) -> None:
    repo = SqlAlchemyFilmRepository(container.session_factory)
    await repo.upsert_many([film])


def test_search_returns_live_results_with_poster_rating_and_description(
    client: TestClient,
) -> None:
    with aioresponses() as mocked:
        mocked.get(
            _SEARCH_URL_PATTERN,
            payload={
                "docs": [
                    {
                        "id": 1,
                        "name": "Матрица",
                        "type": "movie",
                        "year": 1999,
                        "description": "desc",
                        "poster": {"url": "https://example.com/poster.jpg"},
                        "rating": {"kp": 8.7},
                    }
                ]
            },
        )
        response = client.get("/films", params={"query": "матрица"})

    assert response.status_code == 200
    body = response.json()[0]
    assert body["title"] == "Матрица"
    assert body["poster_url"] == "https://example.com/poster.jpg"
    assert body["description"] == "desc"
    assert body["rating"] == 8.7


async def test_search_falls_back_to_the_cache_when_the_provider_returns_nothing(
    client: TestClient, seed_container: Container
) -> None:
    await _seed(
        seed_container,
        Film(id=1, title="Матрица", kind="movie", year=1999, description="d", poster_url=None),
    )

    with aioresponses() as mocked:
        mocked.get(_SEARCH_URL_PATTERN, payload={"docs": []})
        response = client.get("/films", params={"query": "матрица"})

    assert response.status_code == 200
    assert [film["title"] for film in response.json()] == ["Матрица"]


def test_get_film_404_for_an_unknown_id_missing_everywhere(client: TestClient) -> None:
    with aioresponses() as mocked:
        mocked.get(_DETAILS_URL_PATTERN, status=404)
        response = client.get("/films/999999")

    assert response.status_code == 404


async def test_get_film_returns_a_cached_film_without_calling_the_provider(
    client: TestClient, seed_container: Container
) -> None:
    await _seed(
        seed_container,
        Film(id=2, title="Начало", kind="tv-series", year=2010, description="d", poster_url=None),
    )

    # No aioresponses mock registered: a network call here would raise
    # `aiohttp.ClientConnectionError` (no real network access in tests),
    # so this only passes if GetFilmDetails truly checks the cache first.
    response = client.get("/films/2")

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Начало"
    assert body["kind"] == "tv-series"


def test_get_film_falls_back_to_a_live_lookup_when_not_cached(client: TestClient) -> None:
    with aioresponses() as mocked:
        mocked.get(
            _DETAILS_URL_PATTERN,
            payload={"id": 3, "name": "Начало", "type": "movie", "year": 2010},
        )
        response = client.get("/films/3")

    assert response.status_code == 200
    assert response.json()["title"] == "Начало"


def test_search_rejects_a_limit_below_one(client: TestClient) -> None:
    response = client.get("/films", params={"query": "x", "limit": 0})
    assert response.status_code == 422
