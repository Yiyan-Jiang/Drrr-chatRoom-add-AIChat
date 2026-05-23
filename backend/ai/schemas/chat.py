from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    character: Optional[str] = Field(
        None,
        description="AI character key: sakura/rin/mio/yang. Defaults to sakura.",
    )


class AIChatResponse(BaseModel):
    content: str


class AIChatHistoryItem(BaseModel):
    id: int
    character: str
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
