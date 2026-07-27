from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from movielib.domain.entities.review import Review
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.infrastructure.persistence.models import ReviewModel


class SqlAlchemyReviewRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def upsert(self, review: Review) -> None:
        async with self._session_factory() as session:
            model = await session.get(ReviewModel, (int(review.telegram_id), review.film_id))
            if model is None:
                session.add(
                    ReviewModel(
                        telegram_id=int(review.telegram_id),
                        film_id=review.film_id,
                        text=review.text,
                        created_at=review.created_at,
                        updated_at=review.updated_at,
                    )
                )
            else:
                model.text = review.text
                model.updated_at = review.updated_at
            await session.commit()

    async def get(self, telegram_id: TelegramId, film_id: int) -> Review | None:
        async with self._session_factory() as session:
            model = await session.get(ReviewModel, (int(telegram_id), film_id))
            return _to_entity(model) if model is not None else None

    async def delete(self, telegram_id: TelegramId, film_id: int) -> None:
        async with self._session_factory() as session:
            model = await session.get(ReviewModel, (int(telegram_id), film_id))
            if model is not None:
                await session.delete(model)
                await session.commit()

    async def list_for_film(self, film_id: int, *, limit: int = 20) -> list[Review]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ReviewModel)
                .where(ReviewModel.film_id == film_id)
                .order_by(ReviewModel.created_at.desc())
                .limit(limit)
            )
            return [_to_entity(model) for model in result.scalars()]


def _to_entity(model: ReviewModel) -> Review:
    return Review(
        telegram_id=TelegramId(model.telegram_id),
        film_id=model.film_id,
        text=model.text,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
