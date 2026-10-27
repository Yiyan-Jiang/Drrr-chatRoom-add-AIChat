"""校验入口密码并管理门禁 Cookie。"""

import os
from math import ceil
from time import monotonic

from fastapi import APIRouter, Form, HTTPException, Request, Response, status

from common.gate_cookie import (
    GATE_COOKIE_MAX_AGE_SECONDS,
    create_gate_cookie_value,
    is_gate_cookie_valid,
)

router = APIRouter(prefix="/gate", tags=["gate"])

# 当前单进程按客户端地址保存固定失败窗口，首个失败启动计时。
_gate_failures: dict[str, tuple[float, int]] = {}
_FAILURE_WINDOW_SECONDS = 60
_MAX_FAILURES = 5


# 获取本地环境变量密码
def get_gate_password() -> str:
    """读取门禁密码，未配置时返回 HTTP 500。"""
    password = os.environ.get("CHAT_GATE_PASSWORD")
    if not password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CHAT_GATE_PASSWORD is not configured",
        )
    return password


# 校验密码
@router.post("/verify")
async def verify_gate(request: Request, response: Response, password: str = Form(...)):
    """限制客户端在固定窗口内的失败次数，验证成功时写入门禁 Cookie。"""
    now = monotonic()
    for host, (started_at, _) in list(_gate_failures.items()):
        if now - started_at >= _FAILURE_WINDOW_SECONDS:
            del _gate_failures[host]

    host = request.client.host
    started_at, failures = _gate_failures.get(host, (now, 0))
    if failures >= _MAX_FAILURES:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="验证过于频繁，请稍后重试",
            headers={
                "Retry-After": str(ceil(_FAILURE_WINDOW_SECONDS - (now - started_at)))
            },
        )

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
        _gate_failures.pop(host, None)
        return {"success": True}
    _gate_failures[host] = (started_at, failures + 1)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="密码错误")


# 查询gate状态
@router.get("/status")
async def gate_status(request: Request):
    """读取门禁 Cookie 的验证结果，无效时返回 HTTP 401。"""
    gate_passed = request.cookies.get("gate_passed")
    if not is_gate_cookie_valid(gate_passed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="未通过门卫验证"
        )
    return {"verified": True}
