from __future__ import annotations

from movielib.domain.entities.film import Film
from movielib.domain.ports.library_repository import LibraryRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class ListFavorites:
    def __init__(self, library: LibraryRepository) -> None:
        self._library = library

    async def __call__(self, telegram_id: TelegramId) -> list[Film]:
        return await self._library.list_favorites(telegram_id)
