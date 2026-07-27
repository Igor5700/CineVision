from __future__ import annotations

import pytest

from movielib.application.users.register_user import RegisterUser
from movielib.application.users.update_display_name import UpdateDisplayName
from movielib.domain.errors import DomainValidationError, UserNotFoundError
from movielib.domain.value_objects.telegram_id import TelegramId
from tests.unit.fakes.fake_user_repository import FakeUserRepository


async def test_updates_and_persists_the_new_name() -> None:
    users = FakeUserRepository()
    await RegisterUser(users)(TelegramId(1), "ann")

    await UpdateDisplayName(users)(TelegramId(1), "new-name")

    user = await users.get(TelegramId(1))
    assert user is not None
    assert user.username == "new-name"


async def test_rejects_a_blank_name() -> None:
    users = FakeUserRepository()
    await RegisterUser(users)(TelegramId(1), "ann")

    with pytest.raises(DomainValidationError):
        await UpdateDisplayName(users)(TelegramId(1), "   ")


async def test_raises_for_an_unregistered_user() -> None:
    users = FakeUserRepository()

    with pytest.raises(UserNotFoundError):
        await UpdateDisplayName(users)(TelegramId(404), "new-name")
