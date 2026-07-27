from __future__ import annotations

from movielib.domain.entities.film import Film
from movielib.presentation.telegram.keyboards.inline import choose_film_kb


def _film(film_id: int, title: str, year: int | None = 2020) -> Film:
    return Film(id=film_id, title=title, kind="movie", year=year, description=None, poster_url=None)


def test_one_row_per_film_labeled_with_title_and_year() -> None:
    films = [_film(1, "Матрица", 1999), _film(2, "Начало", 2010)]

    markup = choose_film_kb(films)

    assert [row[0].text for row in markup.inline_keyboard] == ["Матрица (1999)", "Начало (2010)"]
    assert [row[0].callback_data for row in markup.inline_keyboard] == [
        "choose_film:1",
        "choose_film:2",
    ]


def test_omits_the_year_when_missing() -> None:
    markup = choose_film_kb([_film(1, "Без года", year=None)])
    assert markup.inline_keyboard[0][0].text == "Без года"


def test_truncates_a_long_title() -> None:
    long_title = "О" * 60
    markup = choose_film_kb([_film(1, long_title, year=2020)])

    label = markup.inline_keyboard[0][0].text
    assert label.endswith("… (2020)")
    assert len(label) < len(long_title)
