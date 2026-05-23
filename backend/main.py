from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv(Path(__file__).parent / ".env")
from fastapi.middleware.cors import CORSMiddleware
from socketio import ASGIApp

from ai.database import init_ai_db
from ai.routers.chat import router as ai_router
from normal_system.bootstrap import init_db
from normal_system.routers import (
    user_router,
    auth_router,
    room_router,
    message_router,
    socket_io_server as sio,
    gate_router,
)

tags_metadata = [
    {
        "name": "users",
        "description": "用户注册与查询（前缀 `/api/users`）。详见项目根目录 `接口文档整理.md`。",
    },
    {
        "name": "auth",
        "description": "登录签发短期 access token（前缀 `/api/auth`）；Socket.IO 连接时在 `auth` 中传 `token`。",
    },
    {
        "name": "rooms",
        "description": "聊天室 CRUD 与分页列表（前缀 `/api/rooms`）。",
    },
    {
        "name": "messages",
        "description": "消息 HTTP 辅助接口（前缀 `/api/messages`）；实时收发以 Socket.IO 为准。",
    },
    {
        "name": "ai",
        "description": "AI 聊天（SSE 流式返回，前缀 `/api/ai`）。",
    },
    {
        "name": "gate",
        "description": "验证是否有正确输入密码 (前缀`/api/gate`)",
    }

]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    await init_ai_db()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Chat Room API",
    description=(
        "登录注册与聊天室 REST API；实时功能通过 Socket.IO（挂载于同一 ASGI 应用根路径）。\n\n"
        "- Swagger UI：`/docs`\n"
        "- ReDoc：`/redoc`\n"
        "- 人文接口说明：`接口文档整理.md`（仓库根目录）"
    ),
    version="0.0.1",
    openapi_tags=tags_metadata,
)


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)


app.include_router(user_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(room_router, prefix="/api")
app.include_router(message_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(gate_router, prefix="/api")


socketio_app = ASGIApp(sio, other_asgi_app=app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:socketio_app", host="127.0.0.1", port=8000, reload=True)
