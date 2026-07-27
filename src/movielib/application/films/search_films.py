from __future__ import annotations

from movielib.domain.entities.film import Film
from movielib.domain.ports.film_metadata_provider import FilmMetadataProvider
from movielib.domain.ports.film_repository import FilmRepository
from movielib.domain.ports.search_history_repository import SearchHistoryRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class SearchFilms:
    def __init__(
        self,
        films: FilmRepository,
        provider: FilmMetadataProvider,
        search_history: SearchHistoryRepository,
    ) -> None:
        self._films = films
        self._provider = provider
        self._search_history = search_history

    async def __call__(
        self, query: str, *, limit: int = 10, telegram_id: TelegramId | None = None
    ) -> list[Film]:
        if telegram_id is not None:
            await self._search_history.log(telegram_id, query)
        found = await self._provider.search_by_name(query)
        if found:
            await self._films.upsert_many(found)
            return found[:limit]
        return await self._films.search_by_title(query, limit=limit)
