from __future__ import annotations

from movielib.domain.entities.user import User
from movielib.domain.errors import UserNotFoundError
from movielib.domain.ports.user_repository import UserRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class GetProfile:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def __call__(self, telegram_id: TelegramId) -> User:
        user = await self._users.get(telegram_id)
        if user is None:
            raise UserNotFoundError(int(telegram_id))
        return user
