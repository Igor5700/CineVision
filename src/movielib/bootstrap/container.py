from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from movielib.application.collections.add_film_to_collection import AddFilmToCollection
from movielib.application.collections.create_collection import CreateCollection
from movielib.application.collections.delete_collection import DeleteCollection
from movielib.application.collections.get_collection import GetCollection
from movielib.application.collections.list_collection_films import ListCollectionFilms
from movielib.application.collections.list_my_collections import ListMyCollections
from movielib.application.collections.remove_film_from_collection import (
    RemoveFilmFromCollection,
)
from movielib.application.films.get_film_details import GetFilmDetails
from movielib.application.films.search_films import SearchFilms
from movielib.application.library.add_favorite import AddFavorite
from movielib.application.library.add_to_watchlist import AddToWatchlist
from movielib.application.library.count_watched import CountWatched
from movielib.application.library.list_favorites import ListFavorites
from movielib.application.library.list_history import ListHistory
from movielib.application.library.list_watchlist import ListWatchlist
from movielib.application.library.mark_watched import MarkWatched
from movielib.application.library.remove_favorite import RemoveFavorite
from movielib.application.library.remove_from_watchlist import RemoveFromWatchlist
from movielib.application.ratings.get_average_rating import GetAverageRating
from movielib.application.ratings.get_my_rating import GetMyRating
from movielib.application.ratings.list_my_ratings import ListMyRatings
from movielib.application.ratings.rate_film import RateFilm
from movielib.application.reviews.delete_review import DeleteReview
from movielib.application.reviews.get_my_review import GetMyReview
from movielib.application.reviews.list_film_reviews import ListFilmReviews
from movielib.application.reviews.write_review import WriteReview
from movielib.application.search.list_recent_searches import ListRecentSearches
from movielib.application.users.get_profile import GetProfile
from movielib.application.users.register_user import RegisterUser
from movielib.application.users.set_birthday import SetBirthday
from movielib.application.users.update_display_name import UpdateDisplayName
from movielib.bootstrap.config import Settings
from movielib.domain.ports.clock import Clock
from movielib.infrastructure.clock_system import SystemClock
from movielib.infrastructure.external.kinopoisk_client import KinopoiskFilmMetadataProvider
from movielib.infrastructure.persistence.collection_repository_sqlalchemy import (
    SqlAlchemyCollectionRepository,
)
from movielib.infrastructure.persistence.engine import create_engine, create_session_factory
from movielib.infrastructure.persistence.film_repository_sqlalchemy import (
    SqlAlchemyFilmRepository,
)
from movielib.infrastructure.persistence.library_repository_sqlalchemy import (
    SqlAlchemyLibraryRepository,
)
from movielib.infrastructure.persistence.rating_repository_sqlalchemy import (
    SqlAlchemyRatingRepository,
)
from movielib.infrastructure.persistence.review_repository_sqlalchemy import (
    SqlAlchemyReviewRepository,
)
from movielib.infrastructure.persistence.search_history_repository_sqlalchemy import (
    SqlAlchemySearchHistoryRepository,
)
from movielib.infrastructure.persistence.user_repository_sqlalchemy import (
    SqlAlchemyUserRepository,
)


@dataclass(slots=True)
class UserUseCases:
    register: RegisterUser
    get_profile: GetProfile
    set_birthday: SetBirthday
    update_display_name: UpdateDisplayName


@dataclass(slots=True)
class FilmUseCases:
    search: SearchFilms
    get_details: GetFilmDetails


@dataclass(slots=True)
class LibraryUseCases:
    add_to_watchlist: AddToWatchlist
    remove_from_watchlist: RemoveFromWatchlist
    list_watchlist: ListWatchlist
    add_favorite: AddFavorite
    remove_favorite: RemoveFavorite
    list_favorites: ListFavorites
    mark_watched: MarkWatched
    list_history: ListHistory
    count_watched: CountWatched


@dataclass(slots=True)
class RatingUseCases:
    rate: RateFilm
    get_mine: GetMyRating
    list_mine: ListMyRatings
    get_average: GetAverageRating


@dataclass(slots=True)
class ReviewUseCases:
    write: WriteReview
    delete: DeleteReview
    get_mine: GetMyReview
    list_for_film: ListFilmReviews


@dataclass(slots=True)
class CollectionUseCases:
    create: CreateCollection
    delete: DeleteCollection
    list_mine: ListMyCollections
    get: GetCollection
    add_film: AddFilmToCollection
    remove_film: RemoveFilmFromCollection
    list_films: ListCollectionFilms


@dataclass(slots=True)
class SearchUseCases:
    list_recent: ListRecentSearches


@dataclass(slots=True)
class UseCases:
    users: UserUseCases
    films: FilmUseCases
    library: LibraryUseCases
    ratings: RatingUseCases
    reviews: ReviewUseCases
    collections: CollectionUseCases
    search: SearchUseCases


@dataclass(slots=True)
class Container:
    settings: Settings
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    use_cases: UseCases
    clock: Clock


def build_container(settings: Settings) -> Container:
    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)

    users = SqlAlchemyUserRepository(session_factory)
    films = SqlAlchemyFilmRepository(session_factory)
    library = SqlAlchemyLibraryRepository(session_factory)
    ratings = SqlAlchemyRatingRepository(session_factory)
    reviews = SqlAlchemyReviewRepository(session_factory)
    collections = SqlAlchemyCollectionRepository(session_factory)
    search_history = SqlAlchemySearchHistoryRepository(session_factory)
    film_provider = KinopoiskFilmMetadataProvider(settings.films_api_token)
    clock = SystemClock()

    use_cases = UseCases(
        users=UserUseCases(
            register=RegisterUser(users),
            get_profile=GetProfile(users),
            set_birthday=SetBirthday(users, clock),
            update_display_name=UpdateDisplayName(users),
        ),
        films=FilmUseCases(
            search=SearchFilms(films, film_provider, search_history),
            get_details=GetFilmDetails(films, film_provider),
        ),
        library=LibraryUseCases(
            add_to_watchlist=AddToWatchlist(library),
            remove_from_watchlist=RemoveFromWatchlist(library),
            list_watchlist=ListWatchlist(library),
            add_favorite=AddFavorite(library),
            remove_favorite=RemoveFavorite(library),
            list_favorites=ListFavorites(library),
            mark_watched=MarkWatched(library),
            list_history=ListHistory(library),
            count_watched=CountWatched(library),
        ),
        ratings=RatingUseCases(
            rate=RateFilm(ratings, clock),
            get_mine=GetMyRating(ratings),
            list_mine=ListMyRatings(ratings),
            get_average=GetAverageRating(ratings),
        ),
        reviews=ReviewUseCases(
            write=WriteReview(reviews, clock),
            delete=DeleteReview(reviews),
            get_mine=GetMyReview(reviews),
            list_for_film=ListFilmReviews(reviews),
        ),
        collections=CollectionUseCases(
            create=CreateCollection(collections, clock),
            delete=DeleteCollection(collections),
            list_mine=ListMyCollections(collections),
            get=GetCollection(collections),
            add_film=AddFilmToCollection(collections),
            remove_film=RemoveFilmFromCollection(collections),
            list_films=ListCollectionFilms(collections),
        ),
        search=SearchUseCases(
            list_recent=ListRecentSearches(search_history),
        ),
    )

    return Container(
        settings=settings,
        engine=engine,
        session_factory=session_factory,
        use_cases=use_cases,
        clock=clock,
    )
