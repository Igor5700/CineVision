from __future__ import annotations

from datetime import date, datetime

from movielib.domain.errors import InvalidBirthdayFormatError, UserNotFoundError
from movielib.domain.ports.clock import Clock
from movielib.domain.ports.user_repository import UserRepository
from movielib.domain.value_objects.telegram_id import TelegramId

_BIRTHDAY_FORMAT = "%d.%m.%Y"


class SetBirthday:
    def __init__(self, users: UserRepository, clock: Clock) -> None:
        self._users = users
        self._clock = clock

    async def __call__(self, telegram_id: TelegramId, raw_birthday: str) -> date:
        birthday = self._parse(raw_birthday)
        user = await self._users.get(telegram_id)
        if user is None:
            raise UserNotFoundError(int(telegram_id))
        user.birthday = birthday
        await self._users.save(user)
        return birthday

    def _parse(self, raw_birthday: str) -> date:
        try:
            parsed = datetime.strptime(raw_birthday.strip(), _BIRTHDAY_FORMAT).date()
        except ValueError as exc:
            raise InvalidBirthdayFormatError(raw_birthday) from exc
        if parsed > self._clock.today():
            raise InvalidBirthdayFormatError(raw_birthday)
        return parsed
