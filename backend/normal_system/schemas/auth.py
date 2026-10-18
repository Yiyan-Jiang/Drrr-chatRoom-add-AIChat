"""定义登录凭据与令牌响应的数据结构。"""

from pydantic import BaseModel

from normal_system.schemas.user import UserPublic


class LoginRequest(BaseModel):
    """接收用户名和密码形式的登录凭据。"""

    username: str
    password: str


class LoginResponse(BaseModel):
    """返回访问令牌、有效时长和当前用户的公开资料。

    Attributes:
        access_token: 登录后签发的访问令牌。
        token_type: 客户端使用令牌的认证类型。
        expires_in: 令牌的有效时长。
        user: 已登录用户的公开资料。
    """

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserPublic
