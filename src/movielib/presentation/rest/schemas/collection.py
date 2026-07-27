from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from movielib.domain.entities.collection import Collection


class CreateCollectionRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None


class CollectionResponse(BaseModel):
    id: int
    telegram_id: int
    name: str
    description: str | None
    created_at: datetime

    @classmethod
    def from_domain(cls, collection: Collection) -> CollectionResponse:
        assert collection.id is not None
        return cls(
            id=collection.id,
            telegram_id=int(collection.telegram_id),
            name=collection.name,
            description=collection.description,
            created_at=collection.created_at,
        )
