# Login and Chat Rooms

一个基于 FastAPI + React + Socket.IO 的登录与聊天室项目。

## 项目概览

这个仓库分成两部分：

- `backend/`：FastAPI 后端，负责用户、登录、房间、消息、门禁校验和 AI 聊天
- `frontend/`：Vite + React 前端，负责页面展示、房间浏览、实时聊天和 AI 对话

核心流程是：

1. 先通过门禁页
2. 注册或登录
3. 进入房间列表
4. 通过 Socket.IO 加入房间并实时收发消息
5. 进入 AI 聊天页，通过 SSE 流式返回内容

## 核心功能

- 用户注册、登录、退出
- 门禁页校验
- 聊天房间列表、创建、查看详情、删除
- 房间内实时消息收发
- AI 聊天，支持多个角色
- 用户数量展示
- 基于 Token 的 Socket.IO 认证

## 技术栈

- 后端：FastAPI、SQLAlchemy、Socket.IO、MySQL、OpenAI SDK
- 前端：React 19、TypeScript、Vite、React Router、Axios、Tailwind CSS、Socket.IO Client

## 目录说明

- `backend/main.py`：后端入口，挂载 REST API 和 Socket.IO
- `backend/routers/`：接口路由
- `backend/models.py`：数据库模型
- `backend/schemas.py`：请求/响应数据结构
- `backend/services/ai_chat.py`：AI 聊天流式输出
- `frontend/src/routers/index.tsx`：前端路由
- `frontend/src/pages/`：页面级组件
- `frontend/src/components/`：通用组件
- `core/init_database.sql`：数据库初始化脚本

## 运行前准备

### 1. 数据库

当前后端使用两个数据库：

- `DATABASE_URL`：普通聊天室库，MySQL，默认库名 `chat_rooms`
- `AI_DATABASE_URL`：AI 聊天历史库，PostgreSQL，默认库名 `ai_chat`

先复制 `backend/.env.example` 为 `backend/.env`，再把其中的数据库密码、门禁密码和密钥改成本机值。

```env
DATABASE_URL=mysql+aiomysql://chat_user:your_password_here@localhost:3306/chat_rooms
AI_DATABASE_URL=postgresql+asyncpg://ai_user:your_password_here@localhost:5432/ai_chat
```

#### MySQL 普通聊天室库

先按需修改 `core/init_database.sql` 里的 `chat_user` 密码，使它和 `backend/.env` 的 `DATABASE_URL` 一致。然后登录 MySQL：

```bash
mysql -u root -p
```

在 MySQL 控制台执行：

```sql
SOURCE D:/python excise/Login and chat rooms/core/init_database.sql;
```

或者使用 Windows 反斜杠路径：

```sql
SOURCE D:\\python excise\\Login and chat rooms\\core\\init_database.sql;
```

#### PostgreSQL AI 聊天历史库

先按需修改 `core/init_ai_database.sql` 里的 `ai_user` 密码，使它和 `backend/.env` 的 `AI_DATABASE_URL` 一致。

如果你在 PowerShell / CMD 这类系统终端里，执行：

```bash
psql -U postgres -f "D:/python excise/Login and chat rooms/core/init_ai_database.sql"
```

或者使用 Windows 反斜杠路径：

```bash
psql -U postgres -f "D:\\python excise\\Login and chat rooms\\core\\init_ai_database.sql"
```

如果你已经进入了 psql 交互窗口，看到 `postgres=#`，不要再输入 `psql -U postgres -f ...`，而是执行：

```sql
\i 'D:/python excise/Login and chat rooms/core/init_ai_database.sql'
```

如果提示符是 `postgres-#`，说明上一条 SQL 还没结束。先按 `Ctrl+C` 取消，或者输入 `\r` 清空当前输入缓冲区，再执行上面的 `\i` 命令。

`core/init_ai_database.sql` 会创建 `ai_chat` 数据库、`ai_user` 用户、`ai_chat_history` 表和 Alembic 版本记录。

### 2. 后端依赖

后端代码当前用到的主要依赖包括：

```bash
pip install fastapi uvicorn sqlalchemy aiomysql asyncpg alembic python-dotenv python-socketio python-multipart openai
```

### 3. 前端依赖

```bash
cd frontend
npm install
```

## 启动方式

### 后端

在 `backend/` 目录下启动：

```bash
cd backend
python main.py
```

默认地址：

- REST API：`http://127.0.0.1:8000/api`
- Swagger：`http://127.0.0.1:8000/docs`

### 前端

在 `frontend/` 目录下启动：

```bash
cd frontend
npm run dev
```

默认地址：

- 前端页面：`http://localhost:5173`

## 环境变量

后端可用环境变量：

- `DATABASE_URL`：后端数据库连接地址
- `AI_DATABASE_URL`：AI 聊天历史数据库连接地址
- `CHAT_GATE_PASSWORD`：门禁页密码
- `CHAT_JWT_SECRET`：登录 token 签名密钥
- `CHAT_ACCESS_TOKEN_EXPIRE_SECONDS`：token 过期时间
- `DEEPSEEK_API_KEY`：AI 聊天所需密钥
- `DEEPSEEK_BASE_URL`：AI 服务地址，默认 `https://api.deepseek.com`

前端可用环境变量：

- `VITE_API_BASE_URL`：后端地址，默认 `http://127.0.0.1:8000`

## 主要路由

- `/gate`：门禁页
- `/login`：登录
- `/register`：注册
- `/home`：主页面
- `/home/rooms`：房间列表
- `/chat/:roomId`：聊天室
- `/ai-chat`：AI 聊天

## 说明

- 实时聊天主要走 Socket.IO，HTTP 接口更多用于初始化、查询和辅助操作。
- AI 聊天使用 SSE 流式返回。
- 当前前端会把 `access_token` 和 `user` 存在 `localStorage`。
- `.env` 不提交到 Git；只提交 `.env.example` 这种不含真实密码的模板。
