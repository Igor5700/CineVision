from __future__ import annotations

import html

from movielib.domain.entities.film import Film
from movielib.domain.entities.review import Review
from movielib.domain.entities.user import User

WELCOME_TEXT = (
    "🎬 Добро пожаловать!\n\n"
    "Здесь вы можете находить фильмы, сохранять их в избранное, вести "
    "собственную коллекцию, получать персональные рекомендации и "
    "отслеживать свою историю просмотров.\n\n"
    "Выберите нужный раздел ниже."
)
CONTACT_TEXT = (
    "Разработчик бота: Игорь Петров.\n\n"
    "Если у вас есть предложения по улучшению Cinevision или вы нашли "
    "неточность в данных о фильме — напишите разработчику напрямую."
)
SUPPORT_TEXT = (
    "Если у вас возникли трудности с ботом, напишите: @inixium\n\n"
    "Отвечаем на вопросы о поиске фильмов, работе личного кабинета, "
    "коллекциями и оценками."
)
LIBRARY_INTRO_TEXT = (
    "Библиотека фильмов Cinevision.\n\n"
    "Ищите фильмы по названию — каждый результат сразу показывает постер, "
    "рейтинг Кинопоиска, жанры, страну, длительность и описание. Сохраняйте "
    "находки в избранное или в список «посмотреть позже», отмечайте "
    "просмотренное, ставьте оценки от 1 до 10, пишите отзывы и собирайте "
    "собственные тематические коллекции.\n\n"
    "Нажмите кнопку ниже, чтобы начать."
)

_FILM_KIND_LABELS = {
    "movie": "Фильм",
    "tv-series": "Сериал",
    "cartoon": "Мультфильм",
    "anime": "Аниме",
    "animated-series": "Мультсериал",
}


def format_profile(
    user: User,
    *,
    watchlist_count: int,
    favorites_count: int,
    watched_count: int,
    ratings_count: int,
    collections_count: int,
) -> str:
    birthday = user.birthday.strftime("%d.%m.%Y") if user.birthday else "не указана"
    username = html.escape(user.username) if user.username else "не указано"
    member_since = user.registered_at.strftime("%d.%m.%Y")
    return (
        f"<b>Личный кабинет</b>\n\n"
        f"Имя: <b>{username}</b>\n"
        f"С нами с: <b>{member_since}</b>\n"
        f"Дата рождения: <b>{birthday}</b>\n"
        f"Баланс: <b>{int(user.balance)}</b>\n\n"
        f"<b>Ваша статистика</b>\n"
        f"Просмотрено фильмов: <b>{watched_count}</b>\n"
        f"В избранном: <b>{favorites_count}</b>\n"
        f"В списке «посмотреть позже»: <b>{watchlist_count}</b>\n"
        f"Оценок поставлено: <b>{ratings_count}</b>\n"
        f"Коллекций создано: <b>{collections_count}</b>"
    )


def format_film_details(
    film: Film, *, my_rating: int | None = None, platform_rating: float | None = None
) -> str:
    year = f" ({film.year})" if film.year is not None else ""
    kind_label = _FILM_KIND_LABELS.get(film.kind)
    kind = kind_label if kind_label is not None else html.escape(film.kind.capitalize())
    description = html.escape(film.description) if film.description else "Описание отсутствует."

    meta = [kind]
    if film.genres:
        meta.append(html.escape(", ".join(film.genres)))
    if film.countries:
        meta.append(html.escape(", ".join(film.countries)))
    if film.duration_minutes is not None:
        meta.append(f"{film.duration_minutes} мин.")
    if film.age_rating is not None:
        meta.append(f"{film.age_rating}+")

    rating_lines = []
    if film.rating is not None:
        rating_lines.append(f"Рейтинг Кинопоиска: <b>{film.rating:.1f}</b>")
    if platform_rating is not None:
        rating_lines.append(f"Рейтинг пользователей Cinevision: <b>{platform_rating:.1f}</b>")
    if my_rating is not None:
        rating_lines.append(f"Ваша оценка: <b>{my_rating}</b>")

    parts = [f"<b>{html.escape(film.title)}</b>{year}", " · ".join(meta)]
    if film.slogan:
        parts.append(f"«{html.escape(film.slogan)}»")
    if rating_lines:
        parts.append("\n".join(rating_lines))
    parts.append(f"<blockquote expandable>{description}</blockquote>")
    return "\n\n".join(parts)


def format_film_list_item(film: Film) -> str:
    year = f" ({film.year})" if film.year is not None else ""
    rating = f" · {film.rating:.1f}" if film.rating is not None else ""
    return f"{html.escape(film.title)}{year}{rating}"


def format_review(review: Review, *, author_label: str) -> str:
    return f"<b>{html.escape(author_label)}</b>\n{html.escape(review.text)}"


def format_recent_searches(queries: list[str]) -> str:
    if not queries:
        return "Вы пока ничего не искали."
    lines = "\n".join(
        f"{position}. {html.escape(query)}" for position, query in enumerate(queries, start=1)
    )
    return f"<b>Недавние запросы</b>\n\n{lines}"


def format_quiz_question(index: int, total: int, prompt: str) -> str:
    return f"<b>Вопрос {index} из {total}</b>\n\n{prompt}"


def format_quiz_summary(labels: list[str]) -> str:
    lines = "\n".join(f"{position}. {label}" for position, label in enumerate(labels, start=1))
    return (
        f"<b>Результаты теста предпочтений</b>\n\n"
        f"Спасибо, что ответили на все вопросы! Вот ваш профиль зрителя:\n\n"
        f"{lines}\n\n"
        f"Мы будем учитывать эти ответы, когда подбираем для вас рекомендации."
    )
