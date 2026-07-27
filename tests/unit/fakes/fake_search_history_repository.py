from __future__ import annotations

from movielib.domain.value_objects.telegram_id import TelegramId


class FakeSearchHistoryRepository:
    def __init__(self) -> None:
        self._by_user: dict[int, list[str]] = {}

    async def log(self, telegram_id: TelegramId, query: str) -> None:
        entries = self._by_user.setdefault(int(telegram_id), [])
        if query in entries:
            entries.remove(query)
        entries.insert(0, query)

    async def list_recent(self, telegram_id: TelegramId, *, limit: int = 10) -> list[str]:
        return self._by_user.get(int(telegram_id), [])[:limit]
