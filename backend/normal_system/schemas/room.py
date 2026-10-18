"""定义房间资料、房主展示和消息响应的数据结构与校验规则。"""

from datetime import datetime
import re
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from normal_system.schemas.message import MessageInDB


ROOM_NAME_PATTERN = re.compile(r"^[\u4e00-\u9fa5A-Za-z0-9_]{1,8}$")


class RoomOwner(BaseModel):
    """返回房主的用户标识、账号和展示资料。"""

    id: int
    username: str
    nickname: Optional[str] = Field(default=None, validate_default=True)
    avatar_key: Optional[str] = None

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


class RoomBase(BaseModel):
    """描述房间资料、年龄条件和人数上限。

    Attributes:
        name: 由汉字、字母、数字或下划线组成的房间名称。
        description: 房间简介。
        notice: 房间公告。
        rules: 房间规则。
        tags: 房间标签。
        min_age: 可选的最低年龄。
        max_age: 可选的最高年龄。
        max_members: 房间人数上限。
    """

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
        """清除房间名称字符串两端的空白。

        Args:
            value: 字段校验前收到的名称值。

        Returns:
            去除两端空白的字符串；非字符串输入原样返回。
        """
        return value.strip() if isinstance(value, str) else value

    @field_validator("name")
    @classmethod
    def validate_name_pattern(cls, value):
        """校验房间名称的字符组成。

        Args:
            value: 已完成字段类型校验的房间名称。

        Returns:
            满足名称格式要求的原始值。

        Raises:
            ValueError: 名称不符合允许的字符和长度规则。
        """
        if not ROOM_NAME_PATTERN.fullmatch(value):
            raise ValueError(
                "room name may only contain Chinese characters, letters, numbers, and underscores"
            )
        return value

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value):
        """将空简介转为空字符串，并清除字符串两端的空白。

        Args:
            value: 字段校验前收到的简介值。

        Returns:
            规范化后的简介；其他类型输入原样返回。
        """
        if value is None:
            return ""
        return value.strip() if isinstance(value, str) else value

    @field_validator("notice", "rules", mode="before")
    @classmethod
    def normalize_text_metadata(cls, value):
        """将公告或规则中的空值转为空字符串。

        Args:
            value: 字段校验前收到的公告或规则值。

        Returns:
            空字符串或非空的原始输入。
        """
        return "" if value is None else value

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value):
        """将标签空值转为空列表。

        Args:
            value: 字段校验前收到的标签值。

        Returns:
            空列表或非空的原始输入。
        """
        return [] if value is None else value

    @field_validator("max_members", mode="before")
    @classmethod
    def normalize_max_members(cls, value):
        """将人数上限空值替换为默认人数。

        Args:
            value: 字段校验前收到的人数上限。

        Returns:
            空值对应默认人数 20，其他输入原样返回。
        """
        return 20 if value is None else value

    @model_validator(mode="after")
    def validate_age_range(self):
        """校验同时提供的年龄上下限顺序。

        Returns:
            通过年龄范围校验的当前房间数据。

        Raises:
            ValueError: 最低年龄大于最高年龄。
        """
        if (
            self.min_age is not None
            and self.max_age is not None
            and self.min_age > self.max_age
        ):
            raise ValueError("min_age must be less than or equal to max_age")
        return self


class RoomCreate(RoomBase):
    """接收创建房间所需的资料和加入条件。"""

    pass


class RoomUpdate(BaseModel):
    """接收可选的房间名称、简介、公告和规则更新。"""

    name: Optional[str] = Field(default=None, min_length=1, max_length=8)
    description: Optional[str] = Field(default=None, max_length=20)
    notice: Optional[str] = Field(default=None, max_length=200)
    rules: Optional[str] = Field(default=None, max_length=200)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value):
        """清除待更新名称字符串两端的空白。

        Args:
            value: 字段校验前收到的名称值。

        Returns:
            去除两端空白的字符串；非字符串输入原样返回。
        """
        return value.strip() if isinstance(value, str) else value

    @field_validator("name")
    @classmethod
    def validate_name_pattern(cls, value):
        """校验非空的待更新房间名称。

        Args:
            value: 已完成字段类型校验的名称或空值。

        Returns:
            满足名称格式要求的原始值或空值。

        Raises:
            ValueError: 非空名称不符合允许的字符和长度规则。
        """
        if value is not None and not ROOM_NAME_PATTERN.fullmatch(value):
            raise ValueError(
                "room name may only contain Chinese characters, letters, numbers, and underscores"
            )
        return value

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value):
        """清除待更新简介字符串两端的空白。

        Args:
            value: 字段校验前收到的简介值。

        Returns:
            去除两端空白的字符串；非字符串输入原样返回。
        """
        return value.strip() if isinstance(value, str) else value


class RoomInDB(RoomBase):
    """返回房间资料、在线人数和可选的房主信息。"""

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
        """将历史在线人数峰值的空值替换为默认值。

        Args:
            value: 字段校验前收到的历史峰值。

        Returns:
            空值对应默认峰值 1，其他输入原样返回。
        """
        return 1 if value is None else value


class RoomWithMessages(RoomInDB):
    """在房间响应中附带消息记录集合。"""

    messages: List[MessageInDB] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
