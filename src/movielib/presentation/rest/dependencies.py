from __future__ import annotations

from fastapi import Request

from movielib.bootstrap.container import Container, UseCases


def get_container(request: Request) -> Container:
    return request.app.state.container  # type: ignore[no-any-return]


def get_use_cases(request: Request) -> UseCases:
    return get_container(request).use_cases
