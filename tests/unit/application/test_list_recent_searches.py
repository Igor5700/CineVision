from __future__ import annotations

from movielib.application.search.list_recent_searches import ListRecentSearches
from movielib.domain.value_objects.telegram_id import TelegramId
from tests.unit.fakes.fake_search_history_repository import FakeSearchHistoryRepository

_USER = TelegramId(1)


async def test_lists_recent_searches_most_recent_first() -> None:
    history = FakeSearchHistoryRepository()
    await history.log(_USER, "матрица")
    await history.log(_USER, "начало")

    results = await ListRecentSearches(history)(_USER)

    assert results == ["начало", "матрица"]


async def test_respects_the_limit() -> None:
    history = FakeSearchHistoryRepository()
    await history.log(_USER, "a")
    await history.log(_USER, "b")

    results = await ListRecentSearches(history)(_USER, limit=1)

    assert results == ["b"]
