from __future__ import annotations

from movielib.domain.ports.library_repository import LibraryRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class RemoveFavorite:
    def __init__(self, library: LibraryRepository) -> None:
        self._library = library

    async def __call__(self, telegram_id: TelegramId, film_id: int) -> None:
        await self._library.remove_favorite(telegram_id, film_id)
