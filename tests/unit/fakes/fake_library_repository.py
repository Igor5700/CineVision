from __future__ import annotations

from datetime import UTC, datetime

from movielib.domain.entities.film import Film
from movielib.domain.value_objects.telegram_id import TelegramId


class FakeLibraryRepository:
    def __init__(self, films_by_id: dict[int, Film] | None = None) -> None:
        self._films_by_id = films_by_id if films_by_id is not None else {}
        self._watchlist: dict[tuple[int, int], datetime] = {}
        self._favorites: dict[tuple[int, int], datetime] = {}
        self._history: dict[tuple[int, int], datetime] = {}

    async def add_to_watchlist(self, telegram_id: TelegramId, film_id: int) -> None:
        self._watchlist[(int(telegram_id), film_id)] = datetime.now(UTC)

    async def remove_from_watchlist(self, telegram_id: TelegramId, film_id: int) -> None:
        self._watchlist.pop((int(telegram_id), film_id), None)

    async def list_watchlist(self, telegram_id: TelegramId) -> list[Film]:
        return self._list(self._watchlist, telegram_id)

    async def add_favorite(self, telegram_id: TelegramId, film_id: int) -> None:
        self._favorites[(int(telegram_id), film_id)] = datetime.now(UTC)

    async def remove_favorite(self, telegram_id: TelegramId, film_id: int) -> None:
        self._favorites.pop((int(telegram_id), film_id), None)

    async def list_favorites(self, telegram_id: TelegramId) -> list[Film]:
        return self._list(self._favorites, telegram_id)

    async def mark_watched(self, telegram_id: TelegramId, film_id: int) -> None:
        self._history[(int(telegram_id), film_id)] = datetime.now(UTC)

    async def list_history(self, telegram_id: TelegramId, *, limit: int = 20) -> list[Film]:
        return self._list(self._history, telegram_id)[:limit]

    async def count_history(self, telegram_id: TelegramId) -> int:
        return sum(1 for uid, _ in self._history if uid == int(telegram_id))

    def _list(
        self, relation: dict[tuple[int, int], datetime], telegram_id: TelegramId
    ) -> list[Film]:
        entries = [
            (film_id, added_at)
            for (uid, film_id), added_at in relation.items()
            if uid == int(telegram_id)
        ]
        entries.sort(key=lambda entry: entry[1], reverse=True)
        return [
            self._films_by_id[film_id] for film_id, _ in entries if film_id in self._films_by_id
        ]
