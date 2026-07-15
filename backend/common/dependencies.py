from fastapi import Header, HTTPException, Request, status

from common.auth import decode_access_token
from common.gate_cookie import is_gate_cookie_valid


async def get_current_user_id(
    authorization: str | None = Header(default=None),
) -> int:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = decode_access_token(token.strip())
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user_id


async def require_gate_passed(request: Request) -> None:
    gate_passed = request.cookies.get("gate_passed")
    if not is_gate_cookie_valid(gate_passed):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Gate verification required")
