<div align="center">

<img src=".github/assets/dollars-logo.png" alt="DOLLARS" width="200" />

# Drrr-chatRoom-add-AIChat

**一个个人练手用的IO项目**

受《无头骑士异闻录》（Durarara!!）中 DOLLARS 聊天室启发，仿照其聊天氛围与视觉风格。

<p>
  <img src=".github/assets/python.svg" alt="Python 3.13" />
  <img src=".github/assets/react.svg" alt="React 19" />
  <img src=".github/assets/typescript.svg" alt="TypeScript 6" />
  <img src=".github/assets/fastapi.svg" alt="FastAPI" />
  <img src=".github/assets/socketio.svg" alt="Socket.IO" />
  <img src=".github/assets/mysql.svg" alt="MySQL 8.4" />
</p>

[功能亮点](#功能亮点) · [快速开始](#快速开始) · [配置说明](#配置说明) · [开发与验证](#开发与验证) · [反馈问题](https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat/issues)

</div>

---

这个项目以《无头骑士异闻录》中的 DOLLARS 聊天室为灵感，将深色界面、角色头像和聊天气泡融入网页聊天室。你可以创建房间、与在线成员聊天，也可以添加好友继续私聊；想留下更完整的内容时，可以发布帖子、评论、点赞和收藏。

前端基于 React + TypeScript，后端使用 FastAPI + Socket.IO，业务数据存储在 MySQL，通过 SQLAlchemy async 与 Alembic 管理数据访问和表结构迁移。

> 当前版本采用单进程架构。仓库名称保留了历史上的 `AIChat`，但当前版本已移除 AI 功能与 PostgreSQL 依赖。

![DOLLARS 平面构成海报：猫耳头盔人物、镂空文字与局部反色蒙版](.github/assets/dollars-poster.png)

## 功能亮点

| 功能           | 你可以做什么                                                           |
| -------------- | ---------------------------------------------------------------------- |
| 门禁与账号     | 通过入口密码进入，注册、登录，并通过 JWT 访问受保护的业务接口。        |
| 房间群聊       | 创建和查找房间，设置简介、标签及人数上限，实时收发消息并查看在线成员。 |
| 好友私聊       | 发送和处理好友申请，建立好友关系后进行一对一聊天，查询历史消息。       |
| 帖子互动       | 发布 Markdown 帖子、发表评论、点赞和收藏，在个人页面查看相关记录。     |
| GitHub 留言板  | 在站内阅读指定仓库的 Issues 和评论，跳转 GitHub 参与讨论。             |
| 消息状态与历史 | 展示发送状态与服务端回执，分页读取历史，重连后通过 HTTP 回补消息。     |

## 快速开始

提供 Docker 开发环境和本地源码运行两种方式。首次使用的流程是：**通过门禁 → 注册账号 → 登录 → 创建或加入房间**。

### 方式一：Docker 开发环境

准备好 Docker 与 Docker Compose，在终端执行：

```bash
git clone https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat.git
cd Drrr-chatRoom-add-AIChat
```

将 [`backend/.env.example`](backend/.env.example) 复制为 `backend/.env`。Windows PowerShell 可使用：

```powershell
Copy-Item backend/.env.example backend/.env
```

修改其中的 `CHAT_GATE_PASSWORD`、`CHAT_GATE_COOKIE_SECRET` 和 `CHAT_JWT_SECRET`，然后在仓库根目录启动：

```bash
docker compose up --build
```

| 入口             | 地址                                                     |
| ---------------- | -------------------------------------------------------- |
| 聊天页面         | [http://localhost:5173](http://localhost:5173)           |
| 后端 API 文档    | [http://localhost:8000/docs](http://localhost:8000/docs) |
| MySQL 宿主机连接 | `127.0.0.1:3307`，数据库 `chat_rooms`                    |

Compose 启动 MySQL、后端和前端。后端在启动前自动应用 Alembic 迁移；容器内的数据库地址由 Compose 覆盖为 `mysql:3306`，无需为此修改 `.env` 的本地地址。

使用 `docker compose down` 停止服务。业务数据保存在 `mysql_data` 数据卷中，保留该卷即可保留数据。

> 此 Compose 配置使用开发服务器和热重载，并包含本地开发数据库凭据。正式部署需要另行配置密钥、数据库凭据和服务入口。

### 方式二：本地源码运行

建议使用与容器及 CI 一致的 **Python 3.13、Node.js 24、MySQL 8.4**。先克隆仓库，在 MySQL 中创建 `chat_rooms` 数据库及具有访问权限的用户，再按上文复制环境配置。

**1. 配置后端**

在 `backend/.env` 中填写自己的数据库连接、门禁密码及签名密钥：

```dotenv
DATABASE_URL=mysql+aiomysql://chat_user:your_password_here@localhost:3306/chat_rooms
CHAT_GATE_PASSWORD=your-gate-password
CHAT_GATE_COOKIE_SECRET=replace-with-your-own-random-secret
CHAT_JWT_SECRET=replace-with-another-random-secret
```

两个签名密钥分别使用至少 32 字节的随机值，不要直接使用上述占位内容。可以分别运行以下命令生成：

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**2. 启动后端**

在仓库根目录打开终端，建议先创建并激活 Python 虚拟环境，再执行：

```bash
cd backend
python -m pip install -r requirements.txt
alembic -c normal_system/alembic.ini upgrade head
python main.py
```

新建数据库使用 Alembic 建表。已有旧版数据库时，先核对表结构与迁移记录，参考 [数据库说明](core/README.md)；不要直接执行 `stamp head` 跳过迁移。

**3. 启动前端**

在仓库根目录另开一个终端：

```bash
cd frontend
npm ci
npm run dev
```

打开 [http://127.0.0.1:5173](http://127.0.0.1:5173)，输入配置的门禁密码，然后注册并登录。后端 API 文档位于 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)。

本地运行时，请统一使用 `localhost` 或 `127.0.0.1` 访问前后端，避免门禁 Cookie 因主机名不同而无法随请求携带。

## 配置说明

后端从 `backend/.env` 读取配置。完整模板见 [`.env.example`](backend/.env.example)。

| 配置项                                       | 用途                                                                           |
| -------------------------------------------- | ------------------------------------------------------------------------------ |
| `DATABASE_URL`                               | MySQL 异步连接串，使用 `mysql+aiomysql://`。                                   |
| `CHAT_GATE_PASSWORD`                         | 入口门禁密码。                                                                 |
| `CHAT_GATE_COOKIE_SECRET`                    | 门禁 Cookie 签名密钥。                                                         |
| `CHAT_JWT_SECRET`                            | 账号访问令牌签名密钥。                                                         |
| `CHAT_ACCESS_TOKEN_EXPIRE_SECONDS`           | 访问令牌有效秒数，默认 `3600`，合法范围为 `60`～`604800`；非法配置会阻止启动。 |
| `GITHUB_ISSUES_OWNER` / `GITHUB_ISSUES_REPO` | 留言板读取的 GitHub 仓库，默认指向本项目。                                     |
| `GITHUB_TOKEN`                               | 可选的 GitHub API 令牌，按需配置仅具有公开仓库读取权限的细粒度令牌。           |

前端默认连接 `http://127.0.0.1:8000`。需要修改时，在 `frontend/.env.local` 中配置并重启 Vite：

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000
```

此地址不包含 `/api`。HTTP API 和 Socket.IO 共用该后端地址；调整前端来源时，还需要核对 [`backend/settings.py`](backend/settings.py) 中的 CORS 配置。

## 项目结构

```text
.
├── .github/
│   ├── assets/                 # README Logo、技术栈徽章与素材来源
│   └── workflows/              # GitHub Actions 冒烟工作流
├── backend/
│   ├── main.py                 # 统一进程入口
│   ├── app_factory.py          # FastAPI、CORS、路由与 Socket.IO 装配
│   ├── common/                 # 认证、门禁与数据库依赖
│   └── normal_system/
│       ├── routers/            # HTTP 入口与 Socket 事件注册
│       ├── services/           # 业务规则与写事务
│       ├── repositories/       # 数据库访问
│       ├── realtime/           # 连接、群聊、私聊与广播
│       ├── integrations/       # GitHub 外部客户端与进程内缓存
│       └── alembic/            # 数据库迁移
├── frontend/src/
│   ├── pages/                  # 页面与路由内容
│   ├── components/             # 页面组件
│   ├── hooks/                  # 状态、聊天历史与连接生命周期
│   ├── api/                    # HTTP API 客户端
│   └── services/socket/        # Socket.IO 连接管理
├── core/                       # 数据库说明与历史 SQL
└── tests/                      # 公开业务入口冒烟与验证说明
```

HTTP 请求通过数据库依赖获取会话，每个 Socket 事件独立创建数据库会话。HTTP 与 Socket 共用业务逻辑；在线成员与广播状态目前保存在单个后端进程中。

## 开发与验证

### 开发环境与提交检查

在仓库根目录安装开发依赖：

```bash
npm install
python -m pip install -r backend/requirements-dev.txt
npm --prefix frontend ci
```

根目录的 `npm install` 会通过 Husky 启用 Git 提交钩子。提交时，lint-staged 只处理暂存文件：前端 JS/TS 使用 Prettier 与 `eslint --fix`，CSS/JSON/HTML 使用 Prettier，后端 Python 使用 `python -m ruff format`。检查失败会阻止提交。

格式化结果会自动加入本次提交，部分暂存文件的未暂存修改会保留。提交后端文件前，请激活已安装 Ruff 的 Python 环境；生产环境只需安装 `backend/requirements.txt`。

<details>
<summary>手动格式化与静态检查命令</summary>

在仓库根目录执行。`format` 会修改文件，`format:check` 和 `--check` 只检查格式。

```bash
npm --prefix frontend run format
npm --prefix frontend run format:check
python -m ruff format backend
python -m ruff format --check backend
npm --prefix frontend run build
npm --prefix frontend run lint
```

这些命令不等同于业务冒烟或页面端到端验证。

</details>

### 业务冒烟

项目只维护冒烟与端到端测试。先启动已应用迁移的 MySQL、后端和前端，并安装前端依赖，然后在仓库根目录运行：

```bash
npm run test:smoke
```

`npm test` 是同一个入口。冒烟通过真实 HTTP / Socket.IO 验证门禁、注册登录、群聊收发与持久化、好友私聊、帖子互动，并清理本次创建的数据。它会读取本地 `backend/.env` 中的门禁密码，请在开发或测试环境运行。

服务地址配置、具体覆盖范围、配置启动冒烟和页面人工 E2E 清单见 [测试说明](tests/README.md)。自动冒烟检查前端入口可用性，浏览器渲染与交互仍需按清单验收。

### GitHub Actions

[`Smoke` 工作流](.github/workflows/smoke.yml) 在 push、Pull Request 和手动触发时执行前端构建、lint 及同一套业务冒烟。工作流启动临时 MySQL、后端和前端，自动生成测试配置，结束后清理，无需提交个人 `.env` 或设置仓库 Secrets。

工作流提交并推送后，可在 [Actions](https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat/actions) 和提交的 Checks 中查看结果。

## 当前范围

当前版本支持消息入库、回执与历史回补，在线状态和实时广播依赖单个后端进程。GitHub 留言板通过后端代理读取外部仓库内容；部分个人资料、设定和帮助页面仍为占位内容。

## 参与项目

欢迎通过 [Issues](https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat/issues) 报告问题或提出建议，也欢迎提交 Pull Request。报告问题时，请提供复现步骤、运行方式和相关日志，并移除密码、令牌等敏感信息。

开发与审查请遵循 [项目协作规范](AGENTS.md)：使用中文说明，只添加与当前变更相关的冒烟或 E2E，提交采用 Conventional Commits，例如：

```text
docs: 完善项目首页与启动说明
```

---

<div align="center">

**找到一个房间，开始一段对话。**

[报告问题](https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat/issues) · [查看源码](https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat) · [回到顶部](#drrr-chatroom-add-aichat)

</div>
