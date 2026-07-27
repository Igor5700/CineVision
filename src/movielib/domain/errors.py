from __future__ import annotations


class DomainError(Exception):
    ...


class DomainValidationError(DomainError):
    ...


class UserNotFoundError(DomainError):
    def __init__(self, telegram_id: int) -> None:
        super().__init__(f"User {telegram_id} not found")
        self.telegram_id = telegram_id


class FilmNotFoundError(DomainError):
    def __init__(self, film_id: int) -> None:
        super().__init__(f"Film {film_id} not found")
        self.film_id = film_id


class InvalidBirthdayFormatError(DomainError):
    def __init__(self, raw_value: str) -> None:
        super().__init__(f"Could not parse birthday: {raw_value!r} (expected dd.mm.yyyy)")
        self.raw_value = raw_value


class QuizAlreadyCompleteError(DomainError):
    ...


class NotAuthorizedError(DomainError):
    def __init__(self, telegram_id: int) -> None:
        super().__init__(f"User {telegram_id} is not authorized to perform this action")
        self.telegram_id = telegram_id


class InvalidRatingScoreError(DomainError):
    def __init__(self, score: int) -> None:
        super().__init__(f"Rating score must be between 1 and 10, got {score}")
        self.score = score


class ReviewNotFoundError(DomainError):
    def __init__(self, telegram_id: int, film_id: int) -> None:
        super().__init__(f"No review by user {telegram_id} for film {film_id}")
        self.telegram_id = telegram_id
        self.film_id = film_id


class CollectionNotFoundError(DomainError):
    def __init__(self, collection_id: int) -> None:
        super().__init__(f"Collection {collection_id} not found")
        self.collection_id = collection_id
