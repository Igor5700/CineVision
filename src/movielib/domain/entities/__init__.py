from movielib.domain.entities.collection import Collection
from movielib.domain.entities.favorite_entry import FavoriteEntry
from movielib.domain.entities.film import Film
from movielib.domain.entities.quiz import (
    QUIZ_QUESTIONS,
    QuizAnswer,
    QuizOption,
    QuizQuestion,
    QuizSession,
    resolve_answer_label,
)
from movielib.domain.entities.rating import Rating
from movielib.domain.entities.review import Review
from movielib.domain.entities.search_history_entry import SearchHistoryEntry
from movielib.domain.entities.user import User
from movielib.domain.entities.viewing_history_entry import ViewingHistoryEntry
from movielib.domain.entities.watchlist_entry import WatchlistEntry

__all__ = [
    "QUIZ_QUESTIONS",
    "Collection",
    "FavoriteEntry",
    "Film",
    "QuizAnswer",
    "QuizOption",
    "QuizQuestion",
    "QuizSession",
    "Rating",
    "Review",
    "SearchHistoryEntry",
    "User",
    "ViewingHistoryEntry",
    "WatchlistEntry",
    "resolve_answer_label",
]
