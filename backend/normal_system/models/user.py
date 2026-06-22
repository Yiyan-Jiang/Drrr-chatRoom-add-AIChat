from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from common.normal_database import Login


_USER_NAME_LEN = 64
_PASSWORD_LEN = 128
_AVATAR_KEY_LEN = 32
_NICKNAME_LEN = 64
_BIO_LEN = 200


class User(Login):
    __tablename__ = "chatRoom_user"
    id: int = Column(Integer, primary_key=True)
    username: str = Column(String(_USER_NAME_LEN), unique=True)
    password: str = Column(String(_PASSWORD_LEN))
    nickname: str = Column(String(_NICKNAME_LEN), nullable=False)
    bio: str = Column(String(_BIO_LEN), nullable=False, default="")
    avatar_key: str = Column(String(_AVATAR_KEY_LEN), default="kanra", nullable=False, index=True)
    created_at: datetime = Column(DateTime, default=datetime.now)
