from __future__ import annotations

from movielib.application.users.register_user import RegisterUser
from movielib.domain.value_objects.telegram_id import TelegramId
from tests.unit.fakes.fake_user_repository import FakeUserRepository


async def test_registers_a_new_user() -> None:
    users = FakeUserRepository()
    register = RegisterUser(users)

    user = await register(TelegramId(1), "ann")

    assert user.username == "ann"
    assert int(user.balance) == 0
    assert await users.get(TelegramId(1)) is not None


async def test_registering_twice_returns_the_existing_user_unchanged() -> None:
    users = FakeUserRepository()
    register = RegisterUser(users)

    first = await register(TelegramId(1), "ann")
    second = await register(TelegramId(1), "someone-else")

    assert second is first
    assert second.username == "ann"
