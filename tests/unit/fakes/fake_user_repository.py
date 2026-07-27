from __future__ import annotations

from movielib.domain.entities.user import User
from movielib.domain.value_objects.telegram_id import TelegramId


class FakeUserRepository:
    def __init__(self) -> None:
        self._users: dict[int, User] = {}

    async def get(self, telegram_id: TelegramId) -> User | None:
        return self._users.get(int(telegram_id))

    async def add(self, user: User) -> None:
        self._users[int(user.telegram_id)] = user

    async def save(self, user: User) -> None:
        self._users[int(user.telegram_id)] = user
