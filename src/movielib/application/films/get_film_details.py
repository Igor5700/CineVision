from __future__ import annotations

from movielib.domain.entities.film import Film
from movielib.domain.errors import FilmNotFoundError
from movielib.domain.ports.film_metadata_provider import FilmMetadataProvider
from movielib.domain.ports.film_repository import FilmRepository


class GetFilmDetails:
    def __init__(self, films: FilmRepository, provider: FilmMetadataProvider) -> None:
        self._films = films
        self._provider = provider

    async def __call__(self, film_id: int) -> Film:
        film = await self._films.get(film_id)
        if film is not None:
            return film
        film = await self._provider.get_by_id(film_id)
        if film is None:
            raise FilmNotFoundError(film_id)
        await self._films.upsert_many([film])
        return film
