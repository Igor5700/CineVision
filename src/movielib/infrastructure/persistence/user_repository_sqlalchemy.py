from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from movielib.domain.entities.user import User
from movielib.domain.value_objects.balance import Balance
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.infrastructure.persistence.models import UserModel


class SqlAlchemyUserRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get(self, telegram_id: TelegramId) -> User | None:
        async with self._session_factory() as session:
            model = await session.get(UserModel, int(telegram_id))
            return _to_entity(model) if model is not None else None

    async def add(self, user: User) -> None:
        async with self._session_factory() as session:
            session.add(_to_model(user))
            await session.commit()

    async def save(self, user: User) -> None:
        async with self._session_factory() as session:
            model = await session.get(UserModel, int(user.telegram_id))
            if model is None:
                session.add(_to_model(user))
            else:
                model.username = user.username
                model.balance = int(user.balance)
                model.birthday = user.birthday
            await session.commit()


def _to_entity(model: UserModel) -> User:
    return User(
        telegram_id=TelegramId(model.telegram_id),
        username=model.username,
        balance=Balance(model.balance),
        registered_at=model.registered_at,
        birthday=model.birthday,
    )


def _to_model(user: User) -> UserModel:
    return UserModel(
        telegram_id=int(user.telegram_id),
        username=user.username,
        balance=int(user.balance),
        registered_at=user.registered_at,
        birthday=user.birthday,
    )
