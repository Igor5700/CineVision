from __future__ import annotations

from aiogram import types


def require_from_user(message: types.Message) -> types.User:
    assert message.from_user is not None
    return message.from_user


def require_user_id(message: types.Message) -> int:
    return require_from_user(message).id


def require_message(callback: types.CallbackQuery) -> types.Message:
    assert isinstance(callback.message, types.Message)
    return callback.message


def require_data(callback: types.CallbackQuery) -> str:
    assert callback.data is not None
    return callback.data
