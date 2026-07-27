from __future__ import annotations

from typing import Protocol

from movielib.domain.entities.review import Review
from movielib.domain.value_objects.telegram_id import TelegramId


class ReviewRepository(Protocol):
    async def upsert(self, review: Review) -> None: ...

    async def get(self, telegram_id: TelegramId, film_id: int) -> Review | None: ...

    async def delete(self, telegram_id: TelegramId, film_id: int) -> None: ...

    async def list_for_film(self, film_id: int, *, limit: int = 20) -> list[Review]: ...
