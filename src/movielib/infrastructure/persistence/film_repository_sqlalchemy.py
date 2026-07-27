from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from movielib.domain.entities.film import Film
from movielib.infrastructure.persistence.models import FilmModel


class SqlAlchemyFilmRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get(self, film_id: int) -> Film | None:
        async with self._session_factory() as session:
            model = await session.get(FilmModel, film_id)
            return film_to_entity(model) if model is not None else None

    async def search_by_title(self, query: str, *, limit: int = 10) -> list[Film]:
        needle = query.strip().lower()
        async with self._session_factory() as session:
            result = await session.execute(
                select(FilmModel).where(FilmModel.search_key.contains(needle)).limit(limit)
            )
            return [film_to_entity(model) for model in result.scalars()]

    async def upsert_many(self, films: list[Film]) -> None:
        if not films:
            return
        async with self._session_factory() as session:
            existing = {
                model.id: model
                for model in (
                    await session.execute(
                        select(FilmModel).where(FilmModel.id.in_([film.id for film in films]))
                    )
                ).scalars()
            }
            for film in films:
                model = existing.get(film.id)
                if model is None:
                    session.add(film_to_model(film))
                else:
                    _apply_film(model, film)
            await session.commit()


def film_to_entity(model: FilmModel) -> Film:
    return Film(
        id=model.id,
        title=model.title,
        kind=model.kind,
        year=model.year,
        description=model.description,
        poster_url=model.poster_url,
        rating=model.rating,
        genres=_split(model.genres),
        countries=_split(model.countries),
        duration_minutes=model.duration_minutes,
        age_rating=model.age_rating,
        slogan=model.slogan,
    )


def film_to_model(film: Film) -> FilmModel:
    return FilmModel(
        id=film.id,
        title=film.title,
        kind=film.kind,
        year=film.year,
        description=film.description,
        poster_url=film.poster_url,
        rating=film.rating,
        genres=_join(film.genres),
        countries=_join(film.countries),
        duration_minutes=film.duration_minutes,
        age_rating=film.age_rating,
        slogan=film.slogan,
        search_key=film.title.lower(),
    )


def _apply_film(model: FilmModel, film: Film) -> None:
    model.title = film.title
    model.kind = film.kind
    model.year = film.year
    model.description = film.description
    model.poster_url = film.poster_url
    model.rating = film.rating
    model.genres = _join(film.genres)
    model.countries = _join(film.countries)
    model.duration_minutes = film.duration_minutes
    model.age_rating = film.age_rating
    model.slogan = film.slogan
    model.search_key = film.title.lower()


def _join(values: list[str]) -> str:
    return ",".join(values)


def _split(value: str) -> list[str]:
    return [v for v in value.split(",") if v]
