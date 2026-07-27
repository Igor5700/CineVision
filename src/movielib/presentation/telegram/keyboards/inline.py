from __future__ import annotations

from aiogram import types

from movielib.domain.entities.collection import Collection
from movielib.domain.entities.film import Film
from movielib.domain.entities.quiz import QuizQuestion

_MAX_BUTTON_TITLE_LENGTH = 40

profile_kb = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [types.InlineKeyboardButton(text="Изменить имя", callback_data="edit_name")],
        [types.InlineKeyboardButton(text="Указать дату рождения", callback_data="set_birthday")],
    ]
)

library_menu_kb = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [types.InlineKeyboardButton(text="Поиск фильма", callback_data="search_film")],
        [types.InlineKeyboardButton(text="Мой список", callback_data="lib:menu:watchlist")],
        [types.InlineKeyboardButton(text="Избранное", callback_data="lib:menu:favorites")],
        [types.InlineKeyboardButton(text="История просмотров", callback_data="lib:menu:history")],
        [types.InlineKeyboardButton(text="Мои коллекции", callback_data="lib:menu:collections")],
        [
            types.InlineKeyboardButton(
                text="Недавние запросы", callback_data="lib:menu:recent_searches"
            )
        ],
    ]
)


def choose_film_kb(films: list[Film]) -> types.InlineKeyboardMarkup:
    rows = [
        [
            types.InlineKeyboardButton(
                text=_button_title(film), callback_data=f"choose_film:{film.id}"
            )
        ]
        for film in films
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=rows)


def _button_title(film: Film) -> str:
    title = film.title
    if len(title) > _MAX_BUTTON_TITLE_LENGTH:
        title = title[: _MAX_BUTTON_TITLE_LENGTH - 1].rstrip() + "…"
    return f"{title} ({film.year})" if film.year is not None else title


def film_actions_kb(film_id: int) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="В список / убрать", callback_data=f"lib:watchlist:{film_id}"
                ),
                types.InlineKeyboardButton(
                    text="В избранное / убрать", callback_data=f"lib:favorite:{film_id}"
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="Просмотрено", callback_data=f"lib:watched:{film_id}"
                ),
                types.InlineKeyboardButton(text="Оценить", callback_data=f"lib:rate:{film_id}"),
            ],
            [
                types.InlineKeyboardButton(
                    text="Написать отзыв", callback_data=f"lib:review:{film_id}"
                ),
                types.InlineKeyboardButton(
                    text="В коллекцию", callback_data=f"lib:pick_collection:{film_id}"
                ),
            ],
        ]
    )


def collections_view_kb(collections: list[Collection]) -> types.InlineKeyboardMarkup:
    rows = [
        [
            types.InlineKeyboardButton(
                text=collection.name, callback_data=f"lib:view_collection:{collection.id}"
            )
        ]
        for collection in collections
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=rows)


def collections_pick_kb(collections: list[Collection], film_id: int) -> types.InlineKeyboardMarkup:
    rows = [
        [
            types.InlineKeyboardButton(
                text=collection.name,
                callback_data=f"lib:add_to_collection:{collection.id}:{film_id}",
            )
        ]
        for collection in collections
    ]
    rows.append(
        [
            types.InlineKeyboardButton(
                text="Новая коллекция", callback_data=f"lib:new_collection:{film_id}"
            )
        ]
    )
    return types.InlineKeyboardMarkup(inline_keyboard=rows)


def quiz_question_kb(question: QuizQuestion) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=option.label, callback_data=f"quiz:{option.code}")]
            for option in question.options
        ]
    )
