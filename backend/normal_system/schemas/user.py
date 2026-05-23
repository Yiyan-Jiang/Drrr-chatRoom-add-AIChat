from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserCountResponse(BaseModel):
    total: int


class UserBase(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    username: Optional[str] = None
    password: Optional[str] = None


class UserInDB(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserPublic(BaseModel):
    id: int
    username: str
    avatar_key: str = "kanra"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
