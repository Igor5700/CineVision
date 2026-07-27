from __future__ import annotations

from movielib.domain.ports.library_repository import LibraryRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class CountWatched:
    def __init__(self, library: LibraryRepository) -> None:
        self._library = library

    async def __call__(self, telegram_id: TelegramId) -> int:
        return await self._library.count_history(telegram_id)
