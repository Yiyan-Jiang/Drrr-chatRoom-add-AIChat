import os

from fastapi import APIRouter, Form, HTTPException, Request, Response, status

from common.gate_cookie import (
    GATE_COOKIE_MAX_AGE_SECONDS,
    create_gate_cookie_value,
    is_gate_cookie_valid,
)

router = APIRouter(prefix="/gate", tags=["gate"])

# 获取本地环境变量密码
def get_gate_password() -> str:
    password = os.environ.get("CHAT_GATE_PASSWORD")
    if not password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CHAT_GATE_PASSWORD is not configured",
        )
    return password

# 校验密码
@router.post("/verify")
async def verify_gate(response: Response, password: str = Form(...)):
    if password == get_gate_password():
        response.set_cookie(
            key="gate_passed",
            value=create_gate_cookie_value(),
            httponly=True,
            max_age=GATE_COOKIE_MAX_AGE_SECONDS,
            samesite="lax",
            path="/",
            secure=False,
        )
        return {"success": True}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="密码错误")

# 查询gate状态
@router.get("/status")
async def gate_status(request: Request):
    gate_passed = request.cookies.get("gate_passed")
    if not is_gate_cookie_valid(gate_passed):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未通过门卫验证")
    return {"verified": True}
