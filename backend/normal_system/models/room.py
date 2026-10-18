"""定义聊天室及其展示资料的持久化结构。"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text

from common.normal_database import Login


_ROOM_NAME_LEN = 8


class Room(Login):
    """保存房间资料、加入条件和房主关联。

    Attributes:
        name: 唯一的房间名称。
        description: 房间简介。
        notice: 房间公告。
        rules: 房间规则。
        tags: 房间标签。
        min_age: 可选的最低年龄。
        max_age: 可选的最高年龄。
        max_members: 房间人数上限。
        peak_online_members: 房间历史在线人数峰值。
        owner_id: 可选的房主用户标识。
        created_at: 房间创建时间。
    """

    __tablename__ = "chatRoom_room"
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(_ROOM_NAME_LEN), unique=True)
    description: str = Column(Text, default="")
    notice: str = Column(Text, default="")
    rules: str = Column(Text, default="")
    tags: list[str] = Column(JSON, default=list)
    min_age: int | None = Column(Integer, nullable=True)
    max_age: int | None = Column(Integer, nullable=True)
    max_members: int = Column(Integer, default=20, nullable=False)
    peak_online_members: int = Column(Integer, default=1, nullable=False)
    owner_id: int | None = Column(
        Integer,
        ForeignKey("chatRoom_user.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    created_at: datetime = Column(DateTime, default=datetime.now)
