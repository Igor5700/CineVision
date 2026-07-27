from __future__ import annotations

from datetime import UTC, datetime

import pytest

from movielib.application.users.register_user import RegisterUser
from movielib.application.users.set_birthday import SetBirthday
from movielib.domain.errors import InvalidBirthdayFormatError, UserNotFoundError
from movielib.domain.value_objects.telegram_id import TelegramId
from tests.unit.fakes.fake_clock import FakeClock
from tests.unit.fakes.fake_user_repository import FakeUserRepository

_TODAY = datetime(2026, 7, 17, tzinfo=UTC)


async def test_sets_a_valid_birthday() -> None:
    users = FakeUserRepository()
    await RegisterUser(users)(TelegramId(1), "ann")
    set_birthday = SetBirthday(users, FakeClock(_TODAY))

    result = await set_birthday(TelegramId(1), "15.06.1995")

    assert result.isoformat() == "1995-06-15"
    user = await users.get(TelegramId(1))
    assert user is not None
    assert user.birthday == result


@pytest.mark.parametrize("raw", ["not-a-date", "31.02.1995", "15/06/1995"])
async def test_rejects_unparseable_or_impossible_dates(raw: str) -> None:
    users = FakeUserRepository()
    await RegisterUser(users)(TelegramId(1), "ann")
    set_birthday = SetBirthday(users, FakeClock(_TODAY))

    with pytest.raises(InvalidBirthdayFormatError):
        await set_birthday(TelegramId(1), raw)


async def test_rejects_a_birthday_in_the_future() -> None:
    users = FakeUserRepository()
    await RegisterUser(users)(TelegramId(1), "ann")
    set_birthday = SetBirthday(users, FakeClock(_TODAY))

    with pytest.raises(InvalidBirthdayFormatError):
        await set_birthday(TelegramId(1), "01.01.2099")


async def test_raises_for_an_unregistered_user() -> None:
    users = FakeUserRepository()
    set_birthday = SetBirthday(users, FakeClock(_TODAY))

    with pytest.raises(UserNotFoundError):
        await set_birthday(TelegramId(404), "15.06.1995")
