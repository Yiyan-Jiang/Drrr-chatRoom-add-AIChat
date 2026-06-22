# Login and Chat Rooms

一个基于 `FastAPI + React + Socket.IO` 的登录与聊天室项目，包含普通聊天和 AI 聊天两套能力。


- 门禁系统：进入应用前的校验页，用来限制访问
- 账号系统：注册、登录、退出和用户信息管理
- 聊天系统：房间列表、进入房间、实时收发消息
- AI 聊天系统：单独的 AI 对话页面，支持流式返

## 技术栈

- 后端：FastAPI、SQLAlchemy、Socket.IO、MySQL、PostgreSQL、OpenAI SDK
- 前端：React、TypeScript、Vite、React Router、Axios、Tailwind CSS、Socket.IO Client

## 运行

后端：

```bash
cd backend
python main.py
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## 数据库初始化

项目里有 2 个初始化 SQL 文件：

- `core/init_database.sql`：普通聊天系统数据
- `core/init_ai_database.sql`：AI 聊天历史数据库

### MySQL

先登录 MySQL，再执
```sql
SOURCE ~/Login and chat rooms/core/init_database.sql;
```

如果你在 Windows 终端里，也可以用反斜杠：

```sql
SOURCE ~\\Login and chat rooms\\core\\init_database.sql;
```

### PostgreSQL

执行 AI 数据库脚本：

```bash
psql -U postgres -f "~/Login and chat rooms/core/init_ai_database.sql"
```

如果已经进入 `psql` 交互界面，也可以直接执行：

```sql
\i '~/Login and chat rooms/core/init_ai_database.sql'
```

## 说明

- 实时聊天主要通过 Socket.IO 实现
- AI 聊天使用流式输出
- 本地配置以 `.env` 为准，按仓库里的示例文件填写即可
- 个人的 review 链接 ： https://fcn5hb1vp409.feishu.cn/wiki/PML1wKbW3iNUr1k1WeVc1mVhnP5?from=from_copylink