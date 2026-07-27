from __future__ import annotations

from movielib.domain.ports.search_history_repository import SearchHistoryRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class ListRecentSearches:
    def __init__(self, search_history: SearchHistoryRepository) -> None:
        self._search_history = search_history

    async def __call__(self, telegram_id: TelegramId, *, limit: int = 10) -> list[str]:
        return await self._search_history.list_recent(telegram_id, limit=limit)
