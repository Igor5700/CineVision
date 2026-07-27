from __future__ import annotations

from dataclasses import dataclass, field

from movielib.domain.errors import DomainValidationError, QuizAlreadyCompleteError
from movielib.domain.value_objects.telegram_id import TelegramId


@dataclass(frozen=True, slots=True)
class QuizOption:
    code: str
    label: str


@dataclass(frozen=True, slots=True)
class QuizQuestion:
    prompt: str
    options: tuple[QuizOption, ...]


QUIZ_QUESTIONS: tuple[QuizQuestion, ...] = (
    QuizQuestion(
        prompt="Какой жанр вам ближе всего?",
        options=(
            QuizOption("fantasy", "Фэнтези и приключения"),
            QuizOption("detective", "Детектив и триллер"),
            QuizOption("roman", "Романтика и драма"),
            QuizOption("comedy", "Комедия"),
        ),
    ),
    QuizQuestion(
        prompt="Какое настроение фильма вам обычно ближе?",
        options=(
            QuizOption("light", "Лёгкое, поднимающее настроение"),
            QuizOption("dark", "Мрачное, напряжённое"),
            QuizOption("thoughtful", "Заставляющее задуматься"),
            QuizOption("epic", "Масштабное, зрелищное"),
        ),
    ),
    QuizQuestion(
        prompt="Фильмы какой эпохи вы предпочитаете?",
        options=(
            QuizOption("classic", "Классику XX века"),
            QuizOption("modern", "Современные новинки"),
            QuizOption("any_era", "Не важно, главное — сюжет"),
        ),
    ),
    QuizQuestion(
        prompt="Кино какой страны или региона вам интереснее?",
        options=(
            QuizOption("hollywood", "Голливуд"),
            QuizOption("russian", "Российское кино"),
            QuizOption("asian", "Азиатское кино"),
            QuizOption("any_country", "Без разницы, страна не главное"),
        ),
    ),
    QuizQuestion(
        prompt="Что вы выбираете чаще: франшизы или отдельные истории?",
        options=(
            QuizOption("franchise", "Франшизы и киновселенные"),
            QuizOption("standalone", "Законченные отдельные фильмы"),
            QuizOption("series", "Сериалы, а не фильмы"),
        ),
    ),
    QuizQuestion(
        prompt="Какая длительность фильма вам комфортна?",
        options=(
            QuizOption("short", "Короче полутора часов"),
            QuizOption("medium", "Стандартные 1.5–2.5 часа"),
            QuizOption("long", "Не пугают и трёхчасовые фильмы"),
        ),
    ),
    QuizQuestion(
        prompt="Какой темп повествования вам нравится?",
        options=(
            QuizOption("fast", "Динамичный, с частыми поворотами"),
            QuizOption("slow", "Медленный, атмосферный"),
            QuizOption("balanced", "Что-то среднее"),
        ),
    ),
    QuizQuestion(
        prompt="С кем вы чаще смотрите фильмы?",
        options=(
            QuizOption("alone", "В одиночестве"),
            QuizOption("partner", "С партнёром"),
            QuizOption("family", "С семьёй, включая детей"),
            QuizOption("friends", "С друзьями"),
        ),
    ),
    QuizQuestion(
        prompt="Как вы относитесь к жёстким сценам (насилие, тяжёлые темы)?",
        options=(
            QuizOption("family_friendly", "Предпочитаю без этого, для всей семьи"),
            QuizOption("moderate", "Спокойно отношусь, если это оправдано сюжетом"),
            QuizOption("no_limits", "Не смущают даже самые жёсткие сцены"),
        ),
    ),
    QuizQuestion(
        prompt="Что вам ближе — пересматривать любимое или искать новое?",
        options=(
            QuizOption("rewatch", "Люблю пересматривать полюбившиеся фильмы"),
            QuizOption("discover", "Всегда ищу что-то новое и неизвестное"),
            QuizOption("mix", "И то, и другое, по настроению"),
        ),
    ),
)


def resolve_answer_label(question_index: int, option_code: str) -> str:
    question = QUIZ_QUESTIONS[question_index]
    for option in question.options:
        if option.code == option_code:
            return option.label
    raise DomainValidationError(f"Unknown option {option_code!r} for question {question_index}")


@dataclass(frozen=True, slots=True)
class QuizAnswer:
    question_index: int
    option_code: str


@dataclass(slots=True)
class QuizSession:
    telegram_id: TelegramId
    answers: list[QuizAnswer] = field(default_factory=list)

    @property
    def next_question_index(self) -> int:
        return len(self.answers)

    def is_complete(self) -> bool:
        return len(self.answers) >= len(QUIZ_QUESTIONS)

    def record_answer(self, option_code: str) -> None:
        if self.is_complete():
            raise QuizAlreadyCompleteError(
                f"Quiz for {self.telegram_id} already has all {len(QUIZ_QUESTIONS)} answers"
            )
        self.answers.append(
            QuizAnswer(question_index=self.next_question_index, option_code=option_code)
        )
