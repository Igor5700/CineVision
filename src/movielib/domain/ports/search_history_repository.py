from __future__ import annotations

from typing import Protocol

from movielib.domain.value_objects.telegram_id import TelegramId


class SearchHistoryRepository(Protocol):
    async def log(self, telegram_id: TelegramId, query: str) -> None: ...

    async def list_recent(self, telegram_id: TelegramId, *, limit: int = 10) -> list[str]: ...
