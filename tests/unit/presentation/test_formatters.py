from __future__ import annotations

from datetime import UTC, datetime

from movielib.domain.entities.film import Film
from movielib.domain.entities.review import Review
from movielib.domain.entities.user import User
from movielib.domain.value_objects.balance import Balance
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.presentation.telegram.formatters import (
    format_film_details,
    format_film_list_item,
    format_profile,
    format_quiz_question,
    format_quiz_summary,
    format_recent_searches,
    format_review,
)


def _user(*, username: str | None = "ann", birthday: object = None) -> User:
    return User(
        telegram_id=TelegramId(1),
        username=username,
        balance=Balance(100),
        registered_at=datetime(2026, 1, 1, tzinfo=UTC),
        birthday=birthday,  # type: ignore[arg-type]
    )


def _profile_text(user: User, **stats: int) -> str:
    defaults = {
        "watchlist_count": 0,
        "favorites_count": 0,
        "watched_count": 0,
        "ratings_count": 0,
        "collections_count": 0,
    }
    return format_profile(user, **{**defaults, **stats})


def _film(
    *,
    title: str = "Матрица",
    kind: str = "movie",
    year: int | None = 1999,
    description: str | None = "desc",
    rating: float | None = None,
    genres: list[str] | None = None,
    countries: list[str] | None = None,
    duration_minutes: int | None = None,
    age_rating: int | None = None,
    slogan: str | None = None,
) -> Film:
    return Film(
        id=1,
        title=title,
        kind=kind,
        year=year,
        description=description,
        poster_url=None,
        rating=rating,
        genres=genres or [],
        countries=countries or [],
        duration_minutes=duration_minutes,
        age_rating=age_rating,
        slogan=slogan,
    )


def test_escapes_a_malicious_display_name() -> None:
    text = _profile_text(_user(username="<b>hacked</b>"))

    assert "&lt;b&gt;hacked&lt;/b&gt;" in text
    assert "<b>hacked</b>" not in text


def test_profile_shows_a_placeholder_for_a_missing_username() -> None:
    text = _profile_text(_user(username=None))
    assert "не указано" in text


def test_profile_shows_a_placeholder_when_birthday_is_unset() -> None:
    text = _profile_text(_user(birthday=None))
    assert "не указана" in text


def test_profile_shows_the_personal_cabinet_title() -> None:
    text = _profile_text(_user())
    assert "<b>Личный кабинет</b>" in text


def test_profile_shows_the_given_stats() -> None:
    text = _profile_text(
        _user(),
        watchlist_count=3,
        favorites_count=5,
        watched_count=12,
        ratings_count=4,
        collections_count=2,
    )

    assert "Просмотрено фильмов: <b>12</b>" in text
    assert "В избранном: <b>5</b>" in text
    assert "«посмотреть позже»: <b>3</b>" in text
    assert "Оценок поставлено: <b>4</b>" in text
    assert "Коллекций создано: <b>2</b>" in text


def test_escapes_a_malicious_film_title() -> None:
    text = format_film_details(_film(title="<script>alert(1)</script>"))

    assert "<script>" not in text
    assert "&lt;script&gt;" in text


def test_film_details_translates_a_known_kind() -> None:
    text = format_film_details(_film(kind="tv-series"))
    assert "Сериал" in text
    assert "tv-series" not in text


def test_film_details_falls_back_to_a_capitalized_unknown_kind() -> None:
    text = format_film_details(_film(kind="documentary"))
    assert "Documentary" in text


def test_film_details_wraps_the_description_in_an_expandable_blockquote() -> None:
    text = format_film_details(_film(description="a long description"))
    assert "<blockquote expandable>a long description</blockquote>" in text


def test_film_details_shows_a_placeholder_for_a_missing_description() -> None:
    text = format_film_details(_film(description=None))
    assert "Описание отсутствует." in text


def test_film_details_omits_the_year_when_missing() -> None:
    text = format_film_details(_film(year=None))
    assert "(" not in text.splitlines()[0]


def test_film_details_shows_genres_countries_duration_and_age_rating() -> None:
    text = format_film_details(
        _film(
            genres=["боевик", "фантастика"],
            countries=["США"],
            duration_minutes=139,
            age_rating=12,
        )
    )
    assert "боевик, фантастика" in text
    assert "США" in text
    assert "139 мин." in text
    assert "12+" in text


def test_film_details_shows_the_slogan_when_present() -> None:
    text = format_film_details(_film(slogan="Добро пожаловать в реальный мир"))
    assert "«Добро пожаловать в реальный мир»" in text


def test_film_details_omits_meta_lines_that_are_unknown() -> None:
    text = format_film_details(_film(genres=[], countries=[], duration_minutes=None, slogan=None))
    assert "«»" not in text
    assert " мин." not in text


def test_quiz_question_numbers_progress() -> None:
    text = format_quiz_question(2, 3, "Где вы предпочитаете смотреть фильмы?")
    assert "Вопрос 2 из 3" in text
    assert "Где вы предпочитаете смотреть фильмы?" in text


def test_quiz_summary_numbers_every_answer() -> None:
    text = format_quiz_summary(["Фэнтези", "Дома"])
    assert "1. Фэнтези" in text
    assert "2. Дома" in text


def test_film_details_shows_the_provider_rating() -> None:
    text = format_film_details(_film(rating=8.7))
    assert "Рейтинг Кинопоиска: <b>8.7</b>" in text


def test_film_details_omits_rating_lines_when_nothing_is_known() -> None:
    text = format_film_details(_film(rating=None))
    assert "Рейтинг" not in text


def test_film_details_shows_platform_rating_and_my_rating() -> None:
    text = format_film_details(_film(rating=None), my_rating=9, platform_rating=7.5)
    assert "Рейтинг пользователей Cinevision: <b>7.5</b>" in text
    assert "Ваша оценка: <b>9</b>" in text


def test_film_list_item_includes_year_and_rating() -> None:
    text = format_film_list_item(_film(title="Матрица", year=1999, rating=8.7))
    assert text == "Матрица (1999) · 8.7"


def test_film_list_item_omits_missing_year_and_rating() -> None:
    text = format_film_list_item(_film(title="Матрица", year=None, rating=None))
    assert text == "Матрица"


def test_review_escapes_malicious_text() -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    review = Review(
        telegram_id=TelegramId(1),
        film_id=1,
        text="<script>alert(1)</script>",
        created_at=now,
        updated_at=now,
    )
    text = format_review(review, author_label="ann")
    assert "<script>" not in text
    assert "&lt;script&gt;" in text


def test_recent_searches_lists_queries_in_order() -> None:
    text = format_recent_searches(["матрица", "начало"])
    assert "1. матрица" in text
    assert "2. начало" in text


def test_recent_searches_shows_a_placeholder_when_empty() -> None:
    text = format_recent_searches([])
    assert "ничего не искали" in text
