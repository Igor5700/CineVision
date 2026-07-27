from __future__ import annotations

from movielib.domain.errors import DomainValidationError, UserNotFoundError
from movielib.domain.ports.user_repository import UserRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class UpdateDisplayName:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def __call__(self, telegram_id: TelegramId, new_name: str) -> None:
        stripped = new_name.strip()
        if not stripped:
            raise DomainValidationError("Display name cannot be blank")

        user = await self._users.get(telegram_id)
        if user is None:
            raise UserNotFoundError(int(telegram_id))
        user.username = stripped
        await self._users.save(user)
