from __future__ import annotations

from movielib.domain.entities.film import Film
from movielib.domain.ports.library_repository import LibraryRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class ListHistory:
    def __init__(self, library: LibraryRepository) -> None:
        self._library = library

    async def __call__(self, telegram_id: TelegramId, *, limit: int = 20) -> list[Film]:
        return await self._library.list_history(telegram_id, limit=limit)
