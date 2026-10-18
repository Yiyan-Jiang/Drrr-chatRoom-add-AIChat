"""定义用户创建、资料更新和公开展示的数据结构与校验规则。"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


AVATAR_KEYS = ("admin", "gray", "kanra", "pink", "setton", "tanaka", "zaika", "zawa")


class UserCountResponse(BaseModel):
    """返回用户总数。"""

    total: int


class UserBase(BaseModel):
    """描述账号创建所需的用户名和密码。"""

    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    """接收新用户的账号凭据。"""

    pass


class UserUpdate(BaseModel):
    """接收昵称、简介和可选头像标识的用户资料更新。"""

    nickname: str = Field(..., min_length=1, max_length=64)
    bio: str = Field(default="", max_length=200)
    avatar_key: Optional[str] = None

    @field_validator("nickname", mode="before")
    @classmethod
    def normalize_nickname(cls, value):
        """清除昵称字符串两端的空白。

        Args:
            value: 字段校验前收到的昵称值。

        Returns:
            去除两端空白的字符串；非字符串输入原样返回。
        """
        return value.strip() if isinstance(value, str) else value

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, value):
        """拒绝空昵称。

        Args:
            value: 已完成字段类型校验的昵称。

        Returns:
            非空的原始昵称。

        Raises:
            ValueError: 昵称为空。
        """
        if not value:
            raise ValueError("nickname must not be empty")
        return value

    @field_validator("bio", mode="before")
    @classmethod
    def normalize_bio(cls, value):
        """将用户简介的空值转为空字符串。

        Args:
            value: 字段校验前收到的简介值。

        Returns:
            空字符串或非空的原始输入。
        """
        return "" if value is None else value

    @field_validator("avatar_key")
    @classmethod
    def validate_avatar_key(cls, value):
        """校验提供的头像标识是否属于预设集合。

        Args:
            value: 已完成字段类型校验的头像标识或空值。

        Returns:
            合法的头像标识或空值。

        Raises:
            ValueError: 提供了预设集合之外的头像标识。
        """
        if value is not None and value not in AVATAR_KEYS:
            raise ValueError("invalid avatar_key")
        return value


class UserInDB(UserBase):
    """描述包含账号凭据、标识和展示资料的用户记录。"""

    id: int
    nickname: Optional[str] = None
    bio: str = ""
    avatar_key: str = "kanra"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    """接收当前用户的昵称、简介和可选头像更新。"""

    nickname: str = Field(..., min_length=1, max_length=64)
    bio: str = Field(default="", max_length=200)
    avatar_key: Optional[str] = None

    @field_validator("nickname", mode="before")
    @classmethod
    def normalize_nickname(cls, value):
        """清除昵称字符串两端的空白。

        Args:
            value: 字段校验前收到的昵称值。

        Returns:
            去除两端空白的字符串；非字符串输入原样返回。
        """
        return value.strip() if isinstance(value, str) else value

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, value):
        """拒绝空昵称。

        Args:
            value: 已完成字段类型校验的昵称。

        Returns:
            非空的原始昵称。

        Raises:
            ValueError: 昵称为空。
        """
        if not value:
            raise ValueError("nickname must not be empty")
        return value

    @field_validator("bio", mode="before")
    @classmethod
    def normalize_bio(cls, value):
        """将用户简介的空值转为空字符串。

        Args:
            value: 字段校验前收到的简介值。

        Returns:
            空字符串或非空的原始输入。
        """
        return "" if value is None else value

    @field_validator("avatar_key")
    @classmethod
    def validate_avatar_key(cls, value):
        """校验提供的头像标识是否属于预设集合。

        Args:
            value: 已完成字段类型校验的头像标识或空值。

        Returns:
            合法的头像标识或空值。

        Raises:
            ValueError: 提供了预设集合之外的头像标识。
        """
        if value is not None and value not in AVATAR_KEYS:
            raise ValueError("invalid avatar_key")
        return value


class UserPublic(BaseModel):
    """返回不含密码的用户公开资料。"""

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
        """在昵称缺失或仅含空白时使用已读取的用户名。

        Args:
            value: 字段校验前收到的昵称值。
            info: 包含已校验用户名的字段校验上下文。

        Returns:
            有效昵称、可用的用户名，或无法替换时的原始值。
        """
        if isinstance(value, str) and value.strip():
            return value
        username = info.data.get("username")
        return username if isinstance(username, str) else value

    @field_validator("bio", mode="before")
    @classmethod
    def normalize_bio(cls, value):
        """将公开资料中简介的空值转为空字符串。

        Args:
            value: 字段校验前收到的简介值。

        Returns:
            空字符串或非空的原始输入。
        """
        return "" if value is None else value
