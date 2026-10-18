"""定义用户账号和公开资料的持久化结构。"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from common.normal_database import Login


_USER_NAME_LEN = 64
_PASSWORD_LEN = 128
_AVATAR_KEY_LEN = 32
_NICKNAME_LEN = 64
_BIO_LEN = 200


class User(Login):
    """保存用户的登录凭据和展示资料。

    Attributes:
        username: 唯一的登录用户名。
        password: 登录凭据的存储值。
        nickname: 用户展示昵称。
        bio: 用户简介。
        avatar_key: 预设头像的标识。
        created_at: 账号创建时间。
    """

    __tablename__ = "chatRoom_user"
    id: int = Column(Integer, primary_key=True)
    username: str = Column(String(_USER_NAME_LEN), unique=True)
    password: str = Column(String(_PASSWORD_LEN))
    nickname: str = Column(String(_NICKNAME_LEN), nullable=False)
    bio: str = Column(String(_BIO_LEN), nullable=False, default="")
    avatar_key: str = Column(
        String(_AVATAR_KEY_LEN), default="kanra", nullable=False, index=True
    )
    created_at: datetime = Column(DateTime, default=datetime.now)
