from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


AVATAR_KEYS = ("admin", "gray", "kanra", "pink", "setton", "tanaka", "zaika", "zawa")


class UserCountResponse(BaseModel):
    total: int


class UserBase(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=64)
    bio: str = Field(default="", max_length=200)
    avatar_key: Optional[str] = None

    @field_validator("nickname", mode="before")
    @classmethod
    def normalize_nickname(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, value):
        if not value:
            raise ValueError("nickname must not be empty")
        return value

    @field_validator("bio", mode="before")
    @classmethod
    def normalize_bio(cls, value):
        return "" if value is None else value

    @field_validator("avatar_key")
    @classmethod
    def validate_avatar_key(cls, value):
        if value is not None and value not in AVATAR_KEYS:
            raise ValueError("invalid avatar_key")
        return value


class UserInDB(UserBase):
    id: int
    nickname: Optional[str] = None
    bio: str = ""
    avatar_key: str = "kanra"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=64)
    bio: str = Field(default="", max_length=200)
    avatar_key: Optional[str] = None

    @field_validator("nickname", mode="before")
    @classmethod
    def normalize_nickname(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, value):
        if not value:
            raise ValueError("nickname must not be empty")
        return value

    @field_validator("bio", mode="before")
    @classmethod
    def normalize_bio(cls, value):
        return "" if value is None else value

    @field_validator("avatar_key")
    @classmethod
    def validate_avatar_key(cls, value):
        if value is not None and value not in AVATAR_KEYS:
            raise ValueError("invalid avatar_key")
        return value


class UserPublic(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = Field(default=None, validate_default=True)
    bio: str = ""
    avatar_key: str = "kanra"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("nickname", mode="before")
    @classmethod
    def default_nickname_to_username(cls, value, info):
        if isinstance(value, str) and value.strip():
            return value
        username = info.data.get("username")
        return username if isinstance(username, str) else value

    @field_validator("bio", mode="before")
    @classmethod
    def normalize_bio(cls, value):
        return "" if value is None else value
