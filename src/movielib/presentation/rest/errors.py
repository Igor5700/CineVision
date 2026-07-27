from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from movielib.domain.errors import (
    CollectionNotFoundError,
    DomainError,
    DomainValidationError,
    FilmNotFoundError,
    InvalidBirthdayFormatError,
    InvalidRatingScoreError,
    NotAuthorizedError,
    QuizAlreadyCompleteError,
    ReviewNotFoundError,
    UserNotFoundError,
)

_STATUS_BY_ERROR_TYPE: dict[type[DomainError], int] = {
    UserNotFoundError: status.HTTP_404_NOT_FOUND,
    FilmNotFoundError: status.HTTP_404_NOT_FOUND,
    ReviewNotFoundError: status.HTTP_404_NOT_FOUND,
    CollectionNotFoundError: status.HTTP_404_NOT_FOUND,
    NotAuthorizedError: status.HTTP_403_FORBIDDEN,
    QuizAlreadyCompleteError: status.HTTP_409_CONFLICT,
    InvalidBirthdayFormatError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    InvalidRatingScoreError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    DomainValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


async def _domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, DomainError)
    code = _STATUS_BY_ERROR_TYPE.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JSONResponse(status_code=code, content={"detail": str(exc)})


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _domain_error_handler)
