from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from movielib.domain.entities.rating import Rating
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.infrastructure.persistence.models import RatingModel


class SqlAlchemyRatingRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def rate(self, rating: Rating) -> None:
        async with self._session_factory() as session:
            model = await session.get(RatingModel, (int(rating.telegram_id), rating.film_id))
            if model is None:
                session.add(
                    RatingModel(
                        telegram_id=int(rating.telegram_id),
                        film_id=rating.film_id,
                        score=rating.score,
                        rated_at=rating.rated_at,
                    )
                )
            else:
                model.score = rating.score
                model.rated_at = rating.rated_at
            await session.commit()

    async def get_my_rating(self, telegram_id: TelegramId, film_id: int) -> Rating | None:
        async with self._session_factory() as session:
            model = await session.get(RatingModel, (int(telegram_id), film_id))
            return _to_entity(model) if model is not None else None

    async def list_my_ratings(self, telegram_id: TelegramId) -> list[Rating]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(RatingModel)
                .where(RatingModel.telegram_id == int(telegram_id))
                .order_by(RatingModel.rated_at.desc())
            )
            return [_to_entity(model) for model in result.scalars()]

    async def average_for_film(self, film_id: int) -> float | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(func.avg(RatingModel.score)).where(RatingModel.film_id == film_id)
            )
            return result.scalar()


def _to_entity(model: RatingModel) -> Rating:
    return Rating(
        telegram_id=TelegramId(model.telegram_id),
        film_id=model.film_id,
        score=model.score,
        rated_at=model.rated_at,
    )
