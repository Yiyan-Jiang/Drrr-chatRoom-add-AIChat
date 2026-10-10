@AGENTS.md

# CLAUDE.md - Login and Chat Rooms 项目规范

> 通用 agent 行为准则见 [AGENTS.md](./AGENTS.md)。本文件是 Claude Code 专属的项目细节约定。

---

## 1. 代码库与本地运行

### 技术栈

| 层面 | 技术 | 说明 |
|------|------|------|
| 后端框架 | FastAPI + Socket.IO | HTTP API 与实时聊天共用一个 ASGI 应用 |
| 后端数据 | SQLAlchemy async + Alembic | MySQL 业务库使用 normal_system 迁移 |
| 认证 | JWT | HTTP Bearer token 与 Socket.IO auth token 共用 |
| 前端框架 | React + TypeScript + Vite | React Router 管理页面路由 |
| 前端通信 | Axios + Socket.IO Client | HTTP API 与实时聊天分开 |
| 样式 | Tailwind CSS + CSS 文件 | 组件内按现有写法延续 |

### 目录职责

- `backend/main.py` - uvicorn 启动入口，运行 `socketio_app`。
- `backend/app_factory.py` - 创建 FastAPI 应用、配置 CORS、挂载业务路由。
- `backend/common/` - JWT、认证依赖、普通数据库连接。
- `backend/normal_system/` - 普通用户、房间、消息、Socket.IO 实时层。
- `backend/normal_system/services/` - 业务规则、用例编排、写事务。
- `backend/normal_system/repositories/` - 按业务拆分的数据库访问。
- `backend/normal_system/realtime/` - Socket 实例、handler 和事件发送。
- `backend/normal_system/integrations/` - GitHub 等外部客户端及现有缓存。
- `frontend/src/api/` - Axios API 封装，统一处理 token 和 401。
- `frontend/src/services/socket/` - 全局 Socket.IO 单例和事件绑定。
- `frontend/src/contexts/AuthContext.tsx` - 登录态、本地 token、Socket 连接生命周期。
- `frontend/src/hooks/` - 群聊、私聊、滚动等状态逻辑。
- `frontend/src/pages/` - 页面入口，负责组装组件和 hook。
- `frontend/src/components/` - 业务组件与通用组件。

---

## 2. 前端分层契约

**层次**：`Pages -> Components -> Hooks -> API/Socket Service -> Types`

### 2.1 Pages 只做 3 件事

1. 从 React Router 读取路由参数和导航能力。
2. 调用 hook 获取状态和动作。
3. 组合组件构建页面布局。

**IMPORTANT：Pages 不要直接拼 HTTP 请求、直接操作 Socket.IO 事件，或复制 hook 中已有的状态机逻辑。**

### 2.2 Components 负责 UI + 交互

- 组件通过 props 接收数据，通过回调通知父层。
- 聊天相关组件延续 `frontend/src/components/chat/` 的拆分方式。
- 房间相关组件延续 `frontend/src/components/room/` 的拆分方式。
- 新增样式优先沿用现有 Tailwind 写法；已有 CSS 文件内的局部样式按原文件风格维护。

### 2.3 Hooks 管理页面状态和副作用

- 普通聊天室状态优先放在 `useRoomChat` 或同层 hook。
- 滚动、分页、乐观消息、ack 超时等副作用不要写进页面组件。
- 新 hook 要返回清晰的 state 与 action，不暴露内部计时器、socket 细节。

### 2.4 API / Socket Service 按协议拆分

- HTTP API 放在 `frontend/src/api/`，统一使用 `apiClient`。
- Socket.IO 事件放在 `frontend/src/services/socket/socketManager.ts`。

---

## 3. 后端分层契约

### 3.1 FastAPI 装配

- 新 HTTP 路由必须通过 `backend/app_factory.py` 的 `include_routers()` 挂载。
- 普通业务路由前缀统一受 `settings.API_PREFIX` 控制。
- Socket.IO 由 `ASGIApp(sio, other_asgi_app=app)` 包装，不要另起第二个服务入口。

### 3.2 普通聊天室域

- REST 协议入口放在 `backend/normal_system/routers/`，写业务调用对应 service，纯查询可直接使用 repository。
- Socket 事件通过 `backend/normal_system/routers/socket.py` 统一注册，处理实现在 `realtime/connection.py`、`room_chat.py` 和 `private_chat.py`。
- 数据库访问通过具体 `normal_system.repositories` 模块，repository 不提交事务、不处理 HTTP 或 Socket 协议。
- service 管理业务规则、提交与回滚；保留唯一键冲突后的回滚和重放行为。
- HTTP 统一使用 `common.normal_database.get_db`；Socket 每个事件使用独立 session，不共享 AsyncSession。
- Socket 实例和广播能力由 `realtime/server.py`、`publisher.py` 提供，HTTP 路由不引用 Socket 路由。
- 在线成员状态使用 `RoomPresence`，不要在前端伪造在线人数。


---

## 4. 认证、协议与数据流

### 4.1 JWT 认证

- 登录接口是 `/api/auth/login`。
- HTTP 请求通过 `Authorization: Bearer <token>` 认证。
- Socket.IO 连接通过 `auth: { token }` 认证。
- token 创建和解析只改 `backend/common/auth.py`，调用方走 `common.dependencies` 或 socket session。

### 4.2 普通聊天室数据流

1. 前端 `AuthContext` 保存 token，并连接 `socketManager`。
2. `ChatRoom` 调用 `useRoomChat(roomId, user, ...)`。
3. 初始房间和历史消息走 HTTP。
4. 加入房间、发送消息、新消息、成员列表走 Socket.IO。
5. 前端用 `client_message_id` 做乐观消息和 ack 合并。


---

## 5. 本地易踩雷约定

| 约定 | 要点 |
|------|------|
| 存储边界 | 当前只使用 MySQL；缓存、Kafka 和新服务进程按已确认的阶段计划引入 |
| Socket 事件名稳定 | 改事件名必须同步后端 socket、前端 socketManager、hook 和测试 |
| token 双通道一致 | HTTP 和 Socket.IO 都依赖同一 JWT 语义 |
| 数据库迁移优先 | 启动时会校验 Alembic revision，不要绕过迁移校验 |
| 前端状态位置 | 页面组装，hook 管状态，api/service 管协议 |
| 历史分页方向 | 聊天视图当前按 head/tail 合并，改滚动逻辑先看 `useChatScroll` |

---

## 6. 路由与页面

### 6.1 前端路由

路由定义在 `frontend/src/routers/index.tsx`。

| 路径 | 页面 | 说明 |
|------|------|------|
| `/gate` | `Ddddr` | 入口门禁 |
| `/login` | `Login` | 登录 |
| `/register` | `Register` | 注册 |
| `/home/rooms` | `RoomSelect` | 房间列表入口 |
| `/chat/:roomId` | `ChatRoom` | 普通聊天室，需要登录 |
| `/news/:slug` | `NewsArticleDetail` | 新闻详情 |
| `/board/:issueNumber` | `MessageBoardIssueDetail` | 留言板详情 |

### 6.2 后端路由

| 前缀 | 文件 | 说明 |
|------|------|------|
| `/api/auth` | `normal_system/routers/auth.py` | 登录签发 JWT |
| `/api/users` | `normal_system/routers/user.py` | 用户相关 |
| `/api/rooms` | `normal_system/routers/room.py` | 房间 CRUD |
| `/api/messages` | `normal_system/routers/message.py` | 消息 HTTP 辅助接口 |
| `/api/gate` | `normal_system/routers/gate.py` | 门禁 |

---

## 7. 跨页面公共能力

| 能力 | 位置 |
|------|------|
| HTTP client / 401 处理 | `frontend/src/api/client.ts` |
| 登录态 / token / socket 生命周期 | `frontend/src/contexts/AuthContext.tsx` |
| Socket.IO 单例 | `frontend/src/services/socket/socketManager.ts` |
| 普通聊天室状态机 | `frontend/src/hooks/useRoomChat.ts` |
| 聊天滚动 | `frontend/src/hooks/useChatScroll.ts` |
| 用户展示名 | `frontend/src/utils/userDisplayName.ts` |
| 房间列表组件 | `frontend/src/components/room/` |
| 聊天消息组件 | `frontend/src/components/chat/` |

判断规则：被 2 个以上页面复用的能力放到 `hooks`、`components/common`、`utils` 或 `api/service`；单页面能力留在对应页面或业务组件目录。

---

## 8. 新页面 / 新组件 / 新 API 起手式

### 新前端页面

1. 在 `frontend/src/pages/` 下选择正确业务目录。
2. 在 `frontend/src/routers/index.tsx` 注册路由，必要时包 `RequireAuth`。
3. 页面只组合 hook 和组件，不直接写协议细节。
4. 如需要服务端数据，先在 `frontend/src/api/` 或对应 hook 中补齐。
5. 验证：`cd frontend && npm run build`。

### 新业务组件

1. 放进对应业务目录，如 `components/chat/`、`components/room/`、`components/layout/`。
2. 定义明确 props 类型。
3. 通过回调向外通知操作，不直接改全局状态。
4. 延续当前 Tailwind / CSS 文件风格。
5. 验证：`cd frontend && npm run build`，按 `tests/README.md` 做对应页面的端到端检查；不新增组件单元测试或源码正则断言。

### 新 HTTP API

1. 后端先定义对应 schema，业务规则放 service，SQL 放 repository，router 只处理协议与错误映射。
2. 通过 `app_factory.py` 已挂载的 router 暴露。
3. 前端在 `frontend/src/api/` 增加封装。
4. 涉及响应结构时同步 `frontend/src/types/chat.ts` 或新增类型文件。
5. 验证：启动真实前后端与已迁移的 MySQL，在仓库根目录运行 `npm run test:smoke`，再跑相关前端构建或 lint。

### 新 Socket.IO 事件

1. 后端在 `normal_system/realtime/` 对应 handler 增加处理，通过 `routers/socket.py` 注册。
2. 前端在 `socketManager.ts` 增加 emit/on/off 封装。
3. 使用方放在 hook 内，不直接写到页面组件。
4. 同步更新类型和生命周期清理逻辑。
5. 验证：在仓库根目录运行 `npm run test:smoke`，并按 `tests/README.md` 用两个浏览器会话检查聊天交互。

## 9. 测试范围

- 只维护端到端测试或冒烟测试，统一入口和场景说明见 [tests/README.md](tests/README.md)。
- 不新增单元测试、集成测试、mock、SQLite 内存库、依赖覆盖或读取源码的结构断言。
- 自动测试通过公开 HTTP / Socket.IO 接口访问真实服务，不直接调用 repository、service、hook 等内部实现。
- 使用临时测试数据并在成功或失败后清理，清理失败也必须报告失败。
- 前端构建与 lint 是静态检查；没有实际业务链路验证证据时，不宣称测试通过。
