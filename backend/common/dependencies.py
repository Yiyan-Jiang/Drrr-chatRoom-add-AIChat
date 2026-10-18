"""提供 HTTP Bearer 身份和门禁 Cookie 校验依赖。"""

from fastapi import Header, HTTPException, Request, status

from common.auth import decode_access_token
from common.gate_cookie import is_gate_cookie_valid


# 校验 token
async def get_current_user_id(
    authorization: str | None = Header(default=None),
) -> int:
    """校验 Bearer 请求头并返回令牌中的用户 ID。"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user_id = decode_access_token(token.strip())
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return user_id


# 校验 cookie
async def require_gate_passed(request: Request) -> None:
    """验证请求中的门禁 Cookie，无效时返回 HTTP 401。"""
    gate_passed = request.cookies.get("gate_passed")
    if not is_gate_cookie_valid(gate_passed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Gate verification required",
        )
