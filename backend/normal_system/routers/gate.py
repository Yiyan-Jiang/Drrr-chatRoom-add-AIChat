import os

from fastapi import APIRouter, Form, HTTPException, Request, Response, status

router = APIRouter(prefix="/gate", tags=["gate"])


def get_gate_password() -> str:
    password = os.environ.get("CHAT_GATE_PASSWORD")
    if not password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CHAT_GATE_PASSWORD is not configured",
        )
    return password


@router.post("/verify")
async def verify_gate(response: Response, password: str = Form(...)):
    if password == get_gate_password():
        response.set_cookie(
            key="gate_passed",
            value="true",
            httponly=True,
            max_age=60 * 60 * 24 * 7,
            samesite="lax",
            path="/",
            secure=False,
        )
        return {"success": True}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="密码错误")


@router.get("/status")
async def gate_status(request: Request):
    gate_passed = request.cookies.get("gate_passed")
    if gate_passed != "true":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未通过门卫验证")
    return {"verified": True}
