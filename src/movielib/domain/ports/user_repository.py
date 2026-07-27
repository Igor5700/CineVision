from __future__ import annotations

from typing import Protocol

from movielib.domain.entities.user import User
from movielib.domain.value_objects.telegram_id import TelegramId


class UserRepository(Protocol):
    async def get(self, telegram_id: TelegramId) -> User | None: ...

    async def add(self, user: User) -> None: ...

    async def save(self, user: User) -> None: ...
