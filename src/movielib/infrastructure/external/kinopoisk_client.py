from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import aiohttp

from movielib.domain.entities.film import Film

logger = logging.getLogger(__name__)

_SEARCH_URL = "https://api.kinopoisk.dev/v1.4/movie/search"
_DETAILS_URL = "https://api.kinopoisk.dev/v1.4/movie/{id}"
_REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)


class KinopoiskFilmMetadataProvider:
    def __init__(self, api_key: str, *, session: aiohttp.ClientSession | None = None) -> None:
        self._api_key = api_key
        self._session = session
        self._owns_session = session is None

    async def search_by_name(self, name: str) -> list[Film]:
        async with self._session_scope() as session:
            return await self._search(session, name)

    async def get_by_id(self, film_id: int) -> Film | None:
        async with self._session_scope() as session:
            return await self._get_by_id(session, film_id)

    @asynccontextmanager
    async def _session_scope(self) -> AsyncIterator[aiohttp.ClientSession]:
        session = self._session or aiohttp.ClientSession(timeout=_REQUEST_TIMEOUT)
        try:
            yield session
        finally:
            if self._owns_session:
                await session.close()

    async def _search(self, session: aiohttp.ClientSession, name: str) -> list[Film]:
        try:
            async with session.get(
                _SEARCH_URL,
                params={"query": name, "limit": "250"},
                headers={"X-API-KEY": self._api_key},
                timeout=_REQUEST_TIMEOUT,
            ) as response:
                if response.status != 200:
                    logger.warning(
                        "Kinopoisk search for %r failed with status %s", name, response.status
                    )
                    return []
                payload = await response.json()
        except (aiohttp.ClientError, TimeoutError):
            logger.exception("Kinopoisk search for %r failed", name)
            return []

        films: list[Film] = []
        for doc in payload.get("docs", []):
            film = _parse_film(doc)
            if film is not None:
                films.append(film)
        return films

    async def _get_by_id(self, session: aiohttp.ClientSession, film_id: int) -> Film | None:
        try:
            async with session.get(
                _DETAILS_URL.format(id=film_id),
                headers={"X-API-KEY": self._api_key},
                timeout=_REQUEST_TIMEOUT,
            ) as response:
                if response.status != 200:
                    logger.warning(
                        "Kinopoisk lookup for id %s failed with status %s", film_id, response.status
                    )
                    return None
                doc = await response.json()
        except (aiohttp.ClientError, TimeoutError):
            logger.exception("Kinopoisk lookup for id %s failed", film_id)
            return None
        return _parse_film(doc)


def _parse_film(doc: dict[str, Any]) -> Film | None:
    film_id = doc.get("id")
    title = doc.get("name") or doc.get("alternativeName") or doc.get("enName")
    if film_id is None or not title:
        return None
    poster = doc.get("poster") or {}
    return Film(
        id=film_id,
        title=title,
        kind=doc.get("type") or "unknown",
        year=doc.get("year"),
        description=doc.get("description"),
        poster_url=poster.get("url"),
        rating=_parse_rating(doc.get("rating") or {}),
        genres=_names(doc.get("genres")),
        countries=_names(doc.get("countries")),
        duration_minutes=doc.get("movieLength"),
        age_rating=doc.get("ageRating"),
        slogan=doc.get("slogan") or None,
    )


def _names(entries: Any) -> list[str]:
    if not isinstance(entries, list):
        return []
    return [entry["name"] for entry in entries if isinstance(entry, dict) and entry.get("name")]


def _parse_rating(rating_doc: dict[str, Any]) -> float | None:
    for key in ("kp", "imdb"):
        value = rating_doc.get(key)
        if isinstance(value, int | float) and value > 0:
            return float(value)
    return None
