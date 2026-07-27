from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class Profile(StatesGroup):
    editing_display_name = State()
    setting_birthday = State()


class Library(StatesGroup):
    searching = State()
    rating = State()
    reviewing = State()
    creating_collection = State()


class Quiz(StatesGroup):
    in_progress = State()
