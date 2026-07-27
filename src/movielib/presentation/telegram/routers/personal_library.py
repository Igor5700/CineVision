from __future__ import annotations

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from movielib.bootstrap.container import UseCases
from movielib.domain.entities.film import Film
from movielib.domain.errors import DomainValidationError
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.presentation.telegram.formatters import format_recent_searches
from movielib.presentation.telegram.guards import require_data, require_message, require_user_id
from movielib.presentation.telegram.keyboards import inline
from movielib.presentation.telegram.states import Library

router = Router(name="personal_library")


def _callback_telegram_id(callback: types.CallbackQuery) -> TelegramId:
    return TelegramId(callback.from_user.id)


async def _show_films(message: types.Message, films: list[Film], *, empty_text: str) -> None:
    if not films:
        await message.answer(text=empty_text)
        return
    await message.answer(
        text=f"Всего: <b>{len(films)}</b>. Выберите фильм:",
        reply_markup=inline.choose_film_kb(films),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "lib:menu:watchlist")
async def show_watchlist(callback: types.CallbackQuery, use_cases: UseCases) -> None:
    await callback.answer()
    films = await use_cases.library.list_watchlist(_callback_telegram_id(callback))
    await _show_films(require_message(callback), films, empty_text="Ваш список пуст.")


@router.callback_query(F.data == "lib:menu:favorites")
async def show_favorites(callback: types.CallbackQuery, use_cases: UseCases) -> None:
    await callback.answer()
    films = await use_cases.library.list_favorites(_callback_telegram_id(callback))
    await _show_films(require_message(callback), films, empty_text="В избранном пока пусто.")


@router.callback_query(F.data == "lib:menu:history")
async def show_history(callback: types.CallbackQuery, use_cases: UseCases) -> None:
    await callback.answer()
    films = await use_cases.library.list_history(_callback_telegram_id(callback))
    await _show_films(
        require_message(callback), films, empty_text="Вы пока ничего не отметили как просмотренное."
    )


@router.callback_query(F.data == "lib:menu:recent_searches")
async def show_recent_searches(callback: types.CallbackQuery, use_cases: UseCases) -> None:
    await callback.answer()
    queries = await use_cases.search.list_recent(_callback_telegram_id(callback))
    await require_message(callback).answer(
        text=format_recent_searches(queries), parse_mode="HTML"
    )


@router.callback_query(F.data == "lib:menu:collections")
async def show_collections(callback: types.CallbackQuery, use_cases: UseCases) -> None:
    await callback.answer()
    collections = await use_cases.collections.list_mine(_callback_telegram_id(callback))
    message = require_message(callback)
    if not collections:
        await message.answer(text="У вас пока нет коллекций.")
        return
    await message.answer(
        text="Ваши коллекции:", reply_markup=inline.collections_view_kb(collections)
    )


@router.callback_query(F.data.startswith("lib:view_collection:"))
async def view_collection(callback: types.CallbackQuery, use_cases: UseCases) -> None:
    await callback.answer()
    collection_id = int(require_data(callback).split(":")[2])
    films = await use_cases.collections.list_films(collection_id)
    await _show_films(require_message(callback), films, empty_text="Эта коллекция пока пуста.")


@router.callback_query(F.data.startswith("lib:watchlist:"))
async def toggle_watchlist(callback: types.CallbackQuery, use_cases: UseCases) -> None:
    film_id = int(require_data(callback).split(":")[2])
    telegram_id = _callback_telegram_id(callback)
    current = await use_cases.library.list_watchlist(telegram_id)
    if any(film.id == film_id for film in current):
        await use_cases.library.remove_from_watchlist(telegram_id, film_id)
        await callback.answer("Убрано из списка")
    else:
        await use_cases.library.add_to_watchlist(telegram_id, film_id)
        await callback.answer("Добавлено в список")


@router.callback_query(F.data.startswith("lib:favorite:"))
async def toggle_favorite(callback: types.CallbackQuery, use_cases: UseCases) -> None:
    film_id = int(require_data(callback).split(":")[2])
    telegram_id = _callback_telegram_id(callback)
    current = await use_cases.library.list_favorites(telegram_id)
    if any(film.id == film_id for film in current):
        await use_cases.library.remove_favorite(telegram_id, film_id)
        await callback.answer("Убрано из избранного")
    else:
        await use_cases.library.add_favorite(telegram_id, film_id)
        await callback.answer("Добавлено в избранное")


@router.callback_query(F.data.startswith("lib:watched:"))
async def mark_watched(callback: types.CallbackQuery, use_cases: UseCases) -> None:
    film_id = int(require_data(callback).split(":")[2])
    await use_cases.library.mark_watched(_callback_telegram_id(callback), film_id)
    await callback.answer("Отмечено как просмотренное")


@router.callback_query(F.data.startswith("lib:rate:"))
async def rate_start(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    film_id = int(require_data(callback).split(":")[2])
    await state.update_data(film_id=film_id)
    await state.set_state(Library.rating)
    await require_message(callback).answer(text="Оцените фильм от 1 до 10:")


@router.message(Library.rating)
async def rate_process(message: types.Message, state: FSMContext, use_cases: UseCases) -> None:
    data = await state.get_data()
    film_id = data["film_id"]
    raw_score = (message.text or "").strip()
    if not raw_score.isdigit():
        await message.answer(text="Введите число от 1 до 10.")
        return
    telegram_id = TelegramId(require_user_id(message))
    try:
        await use_cases.ratings.rate(telegram_id, film_id, int(raw_score))
    except DomainValidationError:
        await message.answer(text="Оценка должна быть числом от 1 до 10.")
        return
    await state.clear()
    await message.answer(text="Спасибо, оценка сохранена.")


@router.callback_query(F.data.startswith("lib:review:"))
async def review_start(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    film_id = int(require_data(callback).split(":")[2])
    await state.update_data(film_id=film_id)
    await state.set_state(Library.reviewing)
    await require_message(callback).answer(text="Напишите отзыв о фильме:")


@router.message(Library.reviewing)
async def review_process(message: types.Message, state: FSMContext, use_cases: UseCases) -> None:
    data = await state.get_data()
    film_id = data["film_id"]
    text = message.text or ""
    telegram_id = TelegramId(require_user_id(message))
    try:
        await use_cases.reviews.write(telegram_id, film_id, text)
    except DomainValidationError:
        await message.answer(
            text="Отзыв не может быть пустым или слишком длинным (до 2000 символов)."
        )
        return
    await state.clear()
    await message.answer(text="Отзыв опубликован.")


@router.callback_query(F.data.startswith("lib:pick_collection:"))
async def pick_collection(
    callback: types.CallbackQuery, state: FSMContext, use_cases: UseCases
) -> None:
    await callback.answer()
    film_id = int(require_data(callback).split(":")[2])
    collections = await use_cases.collections.list_mine(_callback_telegram_id(callback))
    message = require_message(callback)
    if not collections:
        await state.update_data(film_id=film_id)
        await state.set_state(Library.creating_collection)
        await message.answer(text="У вас пока нет коллекций. Введите название новой:")
        return
    await message.answer(
        text="Выберите коллекцию:", reply_markup=inline.collections_pick_kb(collections, film_id)
    )


@router.callback_query(F.data.startswith("lib:new_collection:"))
async def new_collection_start(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    film_id = int(require_data(callback).split(":")[2])
    await state.update_data(film_id=film_id)
    await state.set_state(Library.creating_collection)
    await require_message(callback).answer(text="Введите название новой коллекции:")


@router.message(Library.creating_collection)
async def new_collection_process(
    message: types.Message, state: FSMContext, use_cases: UseCases
) -> None:
    data = await state.get_data()
    film_id = data["film_id"]
    name = message.text or ""
    telegram_id = TelegramId(require_user_id(message))
    try:
        collection = await use_cases.collections.create(telegram_id, name)
    except DomainValidationError:
        await message.answer(text="Название коллекции не может быть пустым.")
        return
    assert collection.id is not None
    await use_cases.collections.add_film(telegram_id, collection.id, film_id)
    await state.clear()
    await message.answer(text=f"Коллекция «{collection.name}» создана, фильм добавлен.")


@router.callback_query(F.data.startswith("lib:add_to_collection:"))
async def add_to_collection(callback: types.CallbackQuery, use_cases: UseCases) -> None:
    _, _, collection_id, film_id = require_data(callback).split(":")
    await use_cases.collections.add_film(
        _callback_telegram_id(callback), int(collection_id), int(film_id)
    )
    await callback.answer("Добавлено в коллекцию")
