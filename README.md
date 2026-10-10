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

## 提交时自动格式化

首次配置开发环境时，在仓库根目录安装提交工具和后端开发依赖，再安装前端依赖：

```bash
npm install
python -m pip install -r backend/requirements-dev.txt
npm --prefix frontend ci
```

根目录的 `npm install` 会通过 Husky 启用 Git 提交钩子。之后每次 `git commit`，lint-staged 只处理本次暂存的文件：前端 JS/TS 先由 Prettier 格式化，再运行 `eslint --fix`；前端 CSS/JSON/HTML 由 Prettier 格式化；后端 Python 由 `python -m ruff format` 格式化。格式化结果自动加入本次提交，部分暂存文件的未暂存修改会保留；任务失败会阻止提交。

提交后端文件时，Git 使用的 Python 环境需要已安装 Ruff；使用虚拟环境时先激活它。Ruff 是开发依赖，生产环境继续安装 `backend/requirements.txt` 即可。

需要手动格式化或检查排版时，在仓库根目录运行：

```bash
npm --prefix frontend run format
npm --prefix frontend run format:check
python -m ruff format backend
python -m ruff format --check backend
```

## Docker 开发环境

先配置 `backend/.env` 中的门禁与 JWT 密钥，再在仓库根目录运行：

```bash
docker compose up --build
```

Compose 只启动 MySQL、后端和前端。MySQL 地址在容器内被覆盖为 `mysql:3306`，宿主机端口为 `3307`。后端启动前自动应用普通业务迁移。

此配置使用开发服务器和热重载，正式部署需要另行配置。停止服务可运行 `docker compose down`；保留 `mysql_data` 数据卷以保留业务数据。

## 验证

项目只维护端到端测试或冒烟测试，不维护单元测试、集成测试或源码结构断言。
自动冒烟通过真实 HTTP / Socket.IO 访问运行中的前后端和 MySQL，复用现有前端依赖，无需安装 pytest 或额外测试框架。

先按上文启动本地服务，或运行 `docker compose up -d --build`。宿主机需 Node.js 22.9+，并已安装前端依赖。
在仓库根目录运行：

```bash
npm run test:smoke
# npm test 是同一个冒烟入口
```

命令自动读取本地 `backend/.env` 的门禁密码；使用其他服务地址时通过环境变量指定。
冒烟覆盖门禁、注册登录、群聊实时收发与持久化、好友私聊、帖子互动，并清理本次创建的数据。
具体环境要求、覆盖范围和页面端到端人工检查见 [测试说明](tests/README.md)。

[GitHub Actions 工作流](.github/workflows/smoke.yml) 在 push、PR 和手动触发时运行构建、lint 及同一套真实服务冒烟。
云端会启动临时 MySQL 和前后端，自动生成测试配置，结束后清理；无需提交个人 `.env` 或配置仓库 Secrets。
工作流文件提交并推送后，可在仓库 Actions / Checks 查看结果。

静态检查另行运行，不等同于冒烟或页面端到端测试通过：

```bash
cd frontend
npm run build
npm run lint
```

## 主要边界

- `backend/main.py`：统一进程入口。
- `backend/app_factory.py`：FastAPI、CORS、路由和 Socket.IO ASGI 装配。
- `backend/common/`：认证和 MySQL 数据库依赖。
- `backend/normal_system/`：用户、房间、消息、好友、帖子和实时通信。
- `normal_system/routers/`：HTTP 协议入口及 Socket 事件注册；现有外部路径保持不变。
- `normal_system/services/`：业务规则及写事务；`repositories/`：具体数据库访问。
- `normal_system/realtime/`：Socket 实例、连接、群聊/私聊处理和广播；HTTP 与 Socket 共用业务逻辑。
- `normal_system/integrations/`：外部客户端及现有缓存，GitHub HTTP 路由保持轻量。
- HTTP 统一使用数据库依赖，每个 Socket 事件独立创建 session，退出时释放连接池。
- `frontend/src/api/`：HTTP API；`frontend/src/services/socket/`：Socket 单例。
- 页面组合 UI，hook 管理状态与连接生命周期。
