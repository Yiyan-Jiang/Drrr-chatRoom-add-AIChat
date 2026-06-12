from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AITurnRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(..., min_length=8, max_length=80)
    session_id: str | None = Field(None, max_length=80)
    message: str = Field(..., min_length=1, max_length=2000)
    character: str | None = None
    metadata: dict[str, Any] | None = None

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message must not be blank")
        return value


class AITurnResponse(BaseModel):
    request_id: str
    session_id: str
    answer: str
    status: str
    trace_id: str | None = None
    error_code: str | None = None


class AITurnHistoryItem(BaseModel):
    id: int
    role: str
    content: str
    character: str | None = None
    sequence_no: int
    created_at: datetime | str


class AITurnHistoryResponse(BaseModel):
    session_id: str | None
    items: list[AITurnHistoryItem]
    has_more: bool
    next_before_sequence_no: int | None = None
