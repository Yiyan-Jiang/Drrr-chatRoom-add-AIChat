# Login and Chat Rooms

基于 FastAPI + React + Socket.IO 的实时聊天项目，包含门禁、账号、群聊、好友私聊、帖子和 GitHub Issues 留言板。

业务数据只使用 MySQL，数据库迁移由 SQLAlchemy async + Alembic 管理。AI 功能及 PostgreSQL 依赖已移除。

后续以消息可靠存储、缓存、Kafka、并发控制、断线补齐和多实例投递为演进方向；目前仍是单进程聊天室，尚未引入 Redis 或 Kafka。

## 本地运行

1. 准备 Python、Node.js 和 MySQL，创建 `chat_rooms` 数据库及有权限访问它的用户。
2. 将 `backend/.env.example` 复制为 `backend/.env`，填写 `DATABASE_URL`、门禁密码、门禁签名密钥和 JWT 密钥。
3. 安装依赖、应用迁移并启动后端：

```bash
cd backend
python -m pip install -r requirements.txt
alembic -c normal_system/alembic.ini upgrade head
python main.py
```

已有旧版数据库时，先检查现有表结构与迁移记录，参考 [数据库说明](core/README.md)，不要直接对不匹配的旧表执行 `stamp head`。

前端默认连接 `http://127.0.0.1:8000`，可通过 `VITE_API_BASE_URL` 修改：

```bash
cd frontend
npm install
npm run dev
```

API 文档：`http://127.0.0.1:8000/docs`。

## Docker 开发环境

先配置 `backend/.env` 中的门禁与 JWT 密钥，再在仓库根目录运行：

```bash
docker compose up --build
```

Compose 只启动 MySQL、后端和前端。MySQL 地址在容器内被覆盖为 `mysql:3306`，宿主机端口为 `3307`。后端启动前自动应用普通业务迁移。

此配置使用开发服务器和热重载，正式部署需要另行配置。停止服务可运行 `docker compose down`；保留 `mysql_data` 数据卷以保留业务数据。

## 验证

后端测试需要额外安装 pytest：

```bash
cd backend
python -m pip install pytest
python -m pytest
```

```bash
cd frontend
npm run build
npm run lint
npm run test:chat-room-lifecycle
npm run test:friend-private-chat
npm run test:github-issues-api
```

## 主要边界

- `backend/main.py`：统一进程入口。
- `backend/app_factory.py`：FastAPI、CORS、路由和 Socket.IO ASGI 装配。
- `backend/common/`：认证和 MySQL 数据库依赖。
- `backend/normal_system/`：用户、房间、消息、好友、帖子和实时通信。
- `frontend/src/api/`：HTTP API；`frontend/src/services/socket/`：Socket 单例。
- 页面组合 UI，hook 管理状态与连接生命周期。
