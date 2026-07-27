from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str | None] = mapped_column(String(64))
    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    birthday: Mapped[date | None] = mapped_column(Date)


class FilmModel(Base):
    __tablename__ = "films"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    poster_url: Mapped[str | None] = mapped_column(String(1024))
    rating: Mapped[float | None] = mapped_column(Float)
    # Comma-joined — genre/country names are short, controlled-vocabulary
    # strings from Kinopoisk, never containing a comma themselves.
    genres: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    countries: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    age_rating: Mapped[int | None] = mapped_column(Integer)
    slogan: Mapped[str | None] = mapped_column(Text)
    # Precomputed, Python-lowercased title. SQLite's LIKE only folds ASCII
    # case, so matching Cyrillic titles case-insensitively has to happen by
    # comparing two already-lowercased strings rather than relying on SQL to
    # lowercase one side of the comparison.
    search_key: Mapped[str] = mapped_column(String(512), nullable=False, index=True)


class WatchlistModel(Base):
    __tablename__ = "watchlist"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    film_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class FavoriteModel(Base):
    __tablename__ = "favorites"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    film_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ViewingHistoryModel(Base):
    __tablename__ = "viewing_history"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    film_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    watched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RatingModel(Base):
    __tablename__ = "ratings"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    film_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    rated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ReviewModel(Base):
    __tablename__ = "reviews"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    film_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CollectionModel(Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CollectionItemModel(Base):
    __tablename__ = "collection_items"

    collection_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    film_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SearchHistoryModel(Base):
    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    query: Mapped[str] = mapped_column(String(256), nullable=False)
    searched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
