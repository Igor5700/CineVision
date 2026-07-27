from __future__ import annotations

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from movielib.bootstrap.container import UseCases
from movielib.domain.errors import FilmNotFoundError
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.presentation.telegram.formatters import LIBRARY_INTRO_TEXT, format_film_details
from movielib.presentation.telegram.guards import require_data, require_message, require_user_id
from movielib.presentation.telegram.keyboards import inline, reply
from movielib.presentation.telegram.states import Library

router = Router(name="library")


@router.message(F.text == reply.LIBRARY_BUTTON)
async def open_library(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text=LIBRARY_INTRO_TEXT, reply_markup=inline.library_menu_kb)


@router.callback_query(F.data == "search_film")
async def search_film_start(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    await require_message(callback).answer(text="Введите название фильма:")
    await state.set_state(Library.searching)


@router.message(Library.searching)
async def search_film_process(
    message: types.Message, state: FSMContext, use_cases: UseCases
) -> None:
    await state.clear()
    query = (message.text or "").strip()
    telegram_id = TelegramId(require_user_id(message))
    films = await use_cases.films.search(query, telegram_id=telegram_id)
    if not films:
        await message.answer(
            text="По этому запросу ничего не найдено. Попробуйте другое название."
        )
        return

    await message.answer(
        text=f"Найдено фильмов: <b>{len(films)}</b>. Выберите нужный:",
        reply_markup=inline.choose_film_kb(films),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("choose_film:"))
async def choose_film(callback: types.CallbackQuery, use_cases: UseCases) -> None:
    await callback.answer()
    message = require_message(callback)
    film_id = int(require_data(callback).split(":")[1])
    telegram_id = TelegramId(callback.from_user.id)

    try:
        film = await use_cases.films.get_details(film_id)
    except FilmNotFoundError:
        await message.answer(text="Этот фильм больше не доступен.")
        return

    my_rating = await use_cases.ratings.get_mine(telegram_id, film_id)
    platform_rating = await use_cases.ratings.get_average(film_id)
    text = format_film_details(
        film,
        my_rating=my_rating.score if my_rating is not None else None,
        platform_rating=platform_rating,
    )
    keyboard = inline.film_actions_kb(film_id)
    if film.poster_url:
        await message.answer_photo(
            photo=film.poster_url, caption=text, parse_mode="HTML", reply_markup=keyboard
        )
    else:
        await message.answer(text=text, parse_mode="HTML", reply_markup=keyboard)
