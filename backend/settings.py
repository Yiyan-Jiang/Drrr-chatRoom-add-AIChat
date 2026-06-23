from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).parent
load_dotenv(BACKEND_ROOT / ".env")

API_PREFIX = "/api"

APP_TITLE = "Chat Room API"
APP_DESCRIPTION = (
    "登录注册与聊天室 REST API；实时功能通过 Socket.IO（挂载于同一 ASGI 应用根路径）。\n\n"
    "- Swagger UI：`/docs`\n"
    "- ReDoc：`/redoc`\n"
    "- 人文接口说明：`接口文档整理.md`（仓库根目录）"
)
APP_VERSION = "0.0.1"

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

OPENAPI_TAGS = [
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
    },
]
