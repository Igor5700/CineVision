from __future__ import annotations

import re
from collections.abc import Iterator

import aiohttp
import pytest
from aioresponses import aioresponses

from movielib.infrastructure.external.kinopoisk_client import KinopoiskFilmMetadataProvider

_URL_PATTERN = re.compile(r"^https://api\.kinopoisk\.dev/v1\.4/movie/search.*")
_DETAILS_URL_PATTERN = re.compile(r"^https://api\.kinopoisk\.dev/v1\.4/movie/\d+$")


@pytest.fixture
def mocked_responses() -> Iterator[aioresponses]:
    with aioresponses() as mocked:
        yield mocked


async def test_parses_a_full_search_result(mocked_responses: aioresponses) -> None:
    mocked_responses.get(
        _URL_PATTERN,
        payload={
            "docs": [
                {
                    "id": 301,
                    "name": "Матрица",
                    "type": "movie",
                    "year": 1999,
                    "description": "desc",
                    "poster": {"url": "https://example.com/poster.jpg"},
                }
            ]
        },
    )
    provider = KinopoiskFilmMetadataProvider(api_key="token")

    films = await provider.search_by_name("matrix")

    assert len(films) == 1
    film = films[0]
    assert film.id == 301
    assert film.title == "Матрица"
    assert film.kind == "movie"
    assert film.year == 1999
    assert film.description == "desc"
    assert film.poster_url == "https://example.com/poster.jpg"


async def test_skips_docs_missing_an_id_or_title(mocked_responses: aioresponses) -> None:
    mocked_responses.get(
        _URL_PATTERN,
        payload={
            "docs": [
                {"id": None, "name": "no id"},
                {"id": 1, "name": ""},
                {"id": 2, "name": "ok"},
            ]
        },
    )
    provider = KinopoiskFilmMetadataProvider(api_key="token")

    films = await provider.search_by_name("query")

    assert [film.id for film in films] == [2]


async def test_falls_back_to_alternative_names(mocked_responses: aioresponses) -> None:
    mocked_responses.get(
        _URL_PATTERN,
        payload={"docs": [{"id": 1, "name": None, "alternativeName": "Alt Title"}]},
    )
    provider = KinopoiskFilmMetadataProvider(api_key="token")

    films = await provider.search_by_name("query")

    assert films[0].title == "Alt Title"


async def test_tolerates_a_missing_poster_and_description(mocked_responses: aioresponses) -> None:
    mocked_responses.get(
        _URL_PATTERN, payload={"docs": [{"id": 1, "name": "ok", "type": "movie"}]}
    )
    provider = KinopoiskFilmMetadataProvider(api_key="token")

    films = await provider.search_by_name("query")

    assert films[0].poster_url is None
    assert films[0].description is None


async def test_returns_empty_list_on_a_non_200_status(mocked_responses: aioresponses) -> None:
    mocked_responses.get(_URL_PATTERN, status=500)
    provider = KinopoiskFilmMetadataProvider(api_key="token")

    films = await provider.search_by_name("query")

    assert films == []


async def test_returns_empty_list_on_a_network_error(mocked_responses: aioresponses) -> None:
    mocked_responses.get(_URL_PATTERN, exception=aiohttp.ClientConnectionError("boom"))

    provider = KinopoiskFilmMetadataProvider(api_key="token")
    films = await provider.search_by_name("query")

    assert films == []


async def test_prefers_the_kp_rating(mocked_responses: aioresponses) -> None:
    mocked_responses.get(
        _URL_PATTERN,
        payload={"docs": [{"id": 1, "name": "ok", "rating": {"kp": 8.7, "imdb": 8.1}}]},
    )
    provider = KinopoiskFilmMetadataProvider(api_key="token")

    films = await provider.search_by_name("query")

    assert films[0].rating == 8.7


async def test_falls_back_to_imdb_rating_when_kp_is_zero(mocked_responses: aioresponses) -> None:
    mocked_responses.get(
        _URL_PATTERN,
        payload={"docs": [{"id": 1, "name": "ok", "rating": {"kp": 0, "imdb": 8.1}}]},
    )
    provider = KinopoiskFilmMetadataProvider(api_key="token")

    films = await provider.search_by_name("query")

    assert films[0].rating == 8.1


async def test_rating_is_none_when_no_rating_data_is_present(
    mocked_responses: aioresponses,
) -> None:
    mocked_responses.get(_URL_PATTERN, payload={"docs": [{"id": 1, "name": "ok"}]})
    provider = KinopoiskFilmMetadataProvider(api_key="token")

    films = await provider.search_by_name("query")

    assert films[0].rating is None


async def test_get_by_id_parses_a_film(mocked_responses: aioresponses) -> None:
    mocked_responses.get(
        _DETAILS_URL_PATTERN,
        payload={"id": 301, "name": "Матрица", "type": "movie", "year": 1999},
    )
    provider = KinopoiskFilmMetadataProvider(api_key="token")

    film = await provider.get_by_id(301)

    assert film is not None
    assert film.id == 301
    assert film.title == "Матрица"


async def test_get_by_id_returns_none_on_a_non_200_status(mocked_responses: aioresponses) -> None:
    mocked_responses.get(_DETAILS_URL_PATTERN, status=404)
    provider = KinopoiskFilmMetadataProvider(api_key="token")

    film = await provider.get_by_id(999999)

    assert film is None


async def test_get_by_id_returns_none_on_a_network_error(mocked_responses: aioresponses) -> None:
    mocked_responses.get(_DETAILS_URL_PATTERN, exception=aiohttp.ClientConnectionError("boom"))
    provider = KinopoiskFilmMetadataProvider(api_key="token")

    film = await provider.get_by_id(1)

    assert film is None
