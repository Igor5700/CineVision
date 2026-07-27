from __future__ import annotations

import pytest

from movielib.application.users.get_profile import GetProfile
from movielib.application.users.register_user import RegisterUser
from movielib.domain.errors import UserNotFoundError
from movielib.domain.value_objects.telegram_id import TelegramId
from tests.unit.fakes.fake_user_repository import FakeUserRepository


async def test_returns_the_registered_user() -> None:
    users = FakeUserRepository()
    await RegisterUser(users)(TelegramId(1), "ann")

    profile = await GetProfile(users)(TelegramId(1))

    assert profile.username == "ann"


async def test_raises_when_user_was_never_registered() -> None:
    users = FakeUserRepository()

    with pytest.raises(UserNotFoundError):
        await GetProfile(users)(TelegramId(404))
