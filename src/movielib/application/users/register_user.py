from __future__ import annotations

from datetime import UTC, datetime

from movielib.domain.entities.user import User
from movielib.domain.ports.user_repository import UserRepository
from movielib.domain.value_objects.balance import Balance
from movielib.domain.value_objects.telegram_id import TelegramId


class RegisterUser:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def __call__(self, telegram_id: TelegramId, username: str | None) -> User:
        existing = await self._users.get(telegram_id)
        if existing is not None:
            return existing

        user = User(
            telegram_id=telegram_id,
            username=username,
            balance=Balance(0),
            registered_at=datetime.now(UTC),
        )
        await self._users.add(user)
        return user
