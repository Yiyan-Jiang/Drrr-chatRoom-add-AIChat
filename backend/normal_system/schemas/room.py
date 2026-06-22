from datetime import datetime
import re
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from normal_system.schemas.message import MessageInDB


ROOM_NAME_PATTERN = re.compile(r"^[\u4e00-\u9fa5A-Za-z0-9_]{1,8}$")


class RoomOwner(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = Field(default=None, validate_default=True)
    avatar_key: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("nickname", mode="before")
    @classmethod
    def default_nickname_to_username(cls, value, info):
        if isinstance(value, str) and value.strip():
            return value
        username = info.data.get("username")
        return username if isinstance(username, str) else value


class RoomBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=8)
    description: str = Field(default="", max_length=20)
    notice: str = Field(default="", max_length=200)
    rules: str = Field(default="", max_length=200)
    tags: List[str] = Field(default_factory=list)
    min_age: Optional[int] = Field(default=None, ge=0)
    max_age: Optional[int] = Field(default=None, ge=0)
    max_members: int = Field(default=20, ge=1)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("name")
    @classmethod
    def validate_name_pattern(cls, value):
        if not ROOM_NAME_PATTERN.fullmatch(value):
            raise ValueError("room name may only contain Chinese characters, letters, numbers, and underscores")
        return value

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value):
        if value is None:
            return ""
        return value.strip() if isinstance(value, str) else value

    @field_validator("notice", "rules", mode="before")
    @classmethod
    def normalize_text_metadata(cls, value):
        return "" if value is None else value

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value):
        return [] if value is None else value

    @field_validator("max_members", mode="before")
    @classmethod
    def normalize_max_members(cls, value):
        return 20 if value is None else value

    @model_validator(mode="after")
    def validate_age_range(self):
        if (
            self.min_age is not None
            and self.max_age is not None
            and self.min_age > self.max_age
        ):
            raise ValueError("min_age must be less than or equal to max_age")
        return self


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=8)
    description: Optional[str] = Field(default=None, max_length=20)
    notice: Optional[str] = Field(default=None, max_length=200)
    rules: Optional[str] = Field(default=None, max_length=200)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("name")
    @classmethod
    def validate_name_pattern(cls, value):
        if value is not None and not ROOM_NAME_PATTERN.fullmatch(value):
            raise ValueError("room name may only contain Chinese characters, letters, numbers, and underscores")
        return value

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value):
        return value.strip() if isinstance(value, str) else value


class RoomInDB(RoomBase):
    id: int
    created_at: datetime
    online_members: int = Field(default=0, ge=0)
    peak_online_members: int = Field(default=1, ge=0)
    owner_id: Optional[int] = None
    owner: Optional[RoomOwner] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("peak_online_members", mode="before")
    @classmethod
    def normalize_peak_online_members(cls, value):
        return 1 if value is None else value


class RoomWithMessages(RoomInDB):
    messages: List[MessageInDB] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
