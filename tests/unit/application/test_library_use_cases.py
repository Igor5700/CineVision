from __future__ import annotations

from movielib.application.library.add_favorite import AddFavorite
from movielib.application.library.add_to_watchlist import AddToWatchlist
from movielib.application.library.list_favorites import ListFavorites
from movielib.application.library.list_history import ListHistory
from movielib.application.library.list_watchlist import ListWatchlist
from movielib.application.library.mark_watched import MarkWatched
from movielib.application.library.remove_favorite import RemoveFavorite
from movielib.application.library.remove_from_watchlist import RemoveFromWatchlist
from movielib.domain.entities.film import Film
from movielib.domain.value_objects.telegram_id import TelegramId
from tests.unit.fakes.fake_library_repository import FakeLibraryRepository

_USER = TelegramId(1)
_FILM = Film(id=101, title="Матрица", kind="movie", year=1999, description=None, poster_url=None)


def _repo() -> FakeLibraryRepository:
    return FakeLibraryRepository(films_by_id={_FILM.id: _FILM})


async def test_watchlist_add_list_remove_round_trip() -> None:
    library = _repo()

    await AddToWatchlist(library)(_USER, _FILM.id)
    assert [film.id for film in await ListWatchlist(library)(_USER)] == [_FILM.id]

    await RemoveFromWatchlist(library)(_USER, _FILM.id)
    assert await ListWatchlist(library)(_USER) == []


async def test_watchlist_is_scoped_per_user() -> None:
    library = _repo()
    await AddToWatchlist(library)(_USER, _FILM.id)

    assert await ListWatchlist(library)(TelegramId(2)) == []


async def test_favorites_add_list_remove_round_trip() -> None:
    library = _repo()

    await AddFavorite(library)(_USER, _FILM.id)
    assert [film.id for film in await ListFavorites(library)(_USER)] == [_FILM.id]

    await RemoveFavorite(library)(_USER, _FILM.id)
    assert await ListFavorites(library)(_USER) == []


async def test_mark_watched_then_list_history() -> None:
    library = _repo()

    await MarkWatched(library)(_USER, _FILM.id)

    assert [film.id for film in await ListHistory(library)(_USER)] == [_FILM.id]


async def test_list_history_respects_the_limit() -> None:
    other_film = Film(
        id=102, title="Начало", kind="movie", year=2010, description=None, poster_url=None
    )
    library = FakeLibraryRepository(films_by_id={_FILM.id: _FILM, other_film.id: other_film})
    await MarkWatched(library)(_USER, _FILM.id)
    await MarkWatched(library)(_USER, other_film.id)

    results = await ListHistory(library)(_USER, limit=1)

    assert len(results) == 1
