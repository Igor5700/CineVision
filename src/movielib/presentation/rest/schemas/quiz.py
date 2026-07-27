from __future__ import annotations

from pydantic import BaseModel

from movielib.domain.entities.quiz import QuizAnswer, QuizOption, QuizQuestion


class QuizAnswerSchema(BaseModel):
    question_index: int
    option_code: str

    @classmethod
    def from_domain(cls, answer: QuizAnswer) -> QuizAnswerSchema:
        return cls(question_index=answer.question_index, option_code=answer.option_code)

    def to_domain(self) -> QuizAnswer:
        return QuizAnswer(question_index=self.question_index, option_code=self.option_code)


class QuizOptionSchema(BaseModel):
    code: str
    label: str

    @classmethod
    def from_domain(cls, option: QuizOption) -> QuizOptionSchema:
        return cls(code=option.code, label=option.label)


class QuizQuestionSchema(BaseModel):
    index: int
    total: int
    prompt: str
    options: list[QuizOptionSchema]

    @classmethod
    def from_domain(cls, index: int, total: int, question: QuizQuestion) -> QuizQuestionSchema:
        return cls(
            index=index,
            total=total,
            prompt=question.prompt,
            options=[QuizOptionSchema.from_domain(option) for option in question.options],
        )


class QuizStepRequest(BaseModel):
    telegram_id: int
    answers: list[QuizAnswerSchema] = []
    option_code: str


class QuizStepResponse(BaseModel):
    is_complete: bool
    answers: list[QuizAnswerSchema]
    next_question: QuizQuestionSchema | None
    summary: list[str] | None
