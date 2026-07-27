from __future__ import annotations

from datetime import UTC, datetime

import pytest

from movielib.domain.entities.rating import Rating
from movielib.domain.errors import InvalidRatingScoreError
from movielib.domain.value_objects.telegram_id import TelegramId


def _rating(score: int) -> Rating:
    return Rating(telegram_id=TelegramId(1), film_id=1, score=score, rated_at=datetime.now(UTC))


@pytest.mark.parametrize("score", [1, 5, 10])
def test_accepts_scores_in_range(score: int) -> None:
    assert _rating(score).score == score


@pytest.mark.parametrize("score", [0, -1, 11, 100])
def test_rejects_scores_out_of_range(score: int) -> None:
    with pytest.raises(InvalidRatingScoreError):
        _rating(score)
