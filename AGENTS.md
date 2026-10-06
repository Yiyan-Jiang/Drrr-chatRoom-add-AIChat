# AGENTS.md

面向所有 AI / agent 协作者（Codex / Claude Code / Cursor / Gemini 等）的通用约定。
本文件是代理主入口；Claude 专用补充见 [CLAUDE.md](./CLAUDE.md)，两份文档需要同步维护。

## 项目定位

本仓库是一个登录 + 聊天室系统，包含群聊、好友私聊和帖子，使用 FastAPI + Socket.IO + React，业务数据只存储在 MySQL。

后续围绕消息可靠存储、缓存、Kafka、并发和分布式投递逐阶段演进；这些能力尚未全部实现。

## 架构决策

- 后端单进程启动，统一入口是 `backend/main.py`。
- `backend/app_factory.py` 负责装配 FastAPI、CORS、路由和 Socket.IO ASGI 包装。
- JWT 是 HTTP API 和 Socket.IO 的共同身份层。
- HTTP 协议入口保留在 `backend/normal_system/routers/`；业务规则和写事务放在 `services/`，数据库访问放在具体 `repositories/` 文件。
- Socket.IO 事件统一通过 `backend/normal_system/routers/socket.py` 注册，处理实现在 `realtime/`，HTTP 路由不要导入 Socket 路由。
- HTTP 复用 `common.normal_database.get_db`，Socket 每个事件独立创建 session；只有 service 管理写入提交与回滚。
- 前端 HTTP 封装在 `frontend/src/api/`，Socket 单例在 `frontend/src/services/socket/`。
- 页面尽量只组装 UI，状态和协议细节放在 hook、api、service 层。

## 目录边界

- `backend/common/`：通用认证、数据库依赖。
- `backend/normal_system/`：普通用户、房间、消息、Socket 实时层。
- `backend/normal_system/services/`：业务规则、用例编排、事务；纯查询无需增加转发 service。
- `backend/normal_system/repositories/`：SQL 与持久化操作；`__init__.py` 仅导出，不放业务实现。
- `backend/normal_system/realtime/`：Socket 实例、连接、群聊/私聊 handler 和 publisher；在线状态沿用 `services/room_presence.py`。
- `backend/normal_system/integrations/`：外部服务客户端及现有缓存，不依赖 HTTP 路由。
- `frontend/src/api/client.ts`：Axios 实例、Bearer token、401 处理。
- `frontend/src/contexts/AuthContext.tsx`：登录态、token、本地存储、Socket 连接生命周期。
- `frontend/src/hooks/useRoomChat.ts`：普通聊天室状态机。
- `frontend/src/routers/index.tsx`：React Router 路由和登录守卫。

## 行为准则

### Think Before Coding

- 请求有 2 种以上合理解释时，先列出来让用户确认。
- 涉及协议、数据库、认证、路由、跨页面状态时，先说明影响面。
- 小 typo、局部样式、单文件轻微调整可以直接做。
- 发现更简单的方案要说清楚，但不要扩大任务范围。

### Simplicity First

- 只写解决当前问题需要的最少代码。
- 不加未被要求的配置项、开关、抽象层或新依赖。
- 能沿用现有 hook、api、service 的，不新建平行体系。
- diff 体积要和需求规模匹配。

### Surgical Changes

- 每行改动都要能追溯到当前请求。
- 修 bug 不顺手做大重构；重构类改动单独提出。
- 只清理自己改动造成的无用 import、变量和测试数据。
- 看到已有 dead code 可以指出，不要擅自删除。

### Goal-Driven Execution

- 多步任务先列 `step -> verify` 计划。
- 修 bug：先复现或定位，再修复，再验证。
- 新功能：先确认数据流和边界，再实现，再跑对应验证。
- 跑不起来或没有验证证据时，不要宣称完成。

## 何时直接做 / 何时先问

可以直接做：

- 单文件单点修改。
- 文案、样式、类型小修。
- 有明确复现路径的 bug。
- 按现有模式新增同类 API、hook、组件或测试。

必须先问：

- API 请求参数、响应字段、错误码发生变化。
- Socket.IO 事件名或 payload 结构发生变化。
- JWT、gate、登录态、房间权限、消息归属逻辑发生变化。
- `backend/common/` 与 `normal_system/` 的职责边界发生变化，或引入新的存储、消息中间件和服务进程。
- 数据库 schema、迁移、初始化逻辑发生变化。
- 任务有 2 种以上合理产品解释。

## 完成自检

- [ ] diff 中没有无关格式化、重命名或顺手重构。
- [ ] 改动仍符合 `backend/common` 与 `normal_system` 的职责边界。
- [ ] 前端页面没有直接绕过 `api`、`hook`、`socketManager` 去写协议细节。
- [ ] 协议变更已同步后端 router/socket、前端 `types`、api/service/hook。
- [ ] 认证、权限、房间存在性、消息归属检查没有被绕过。
- [ ] 已运行和改动相关的验证命令，并记录结果。

## 可验证规则

所有关键变更都要能被命令验证。按改动范围选择，不要求每次全跑。

```bash
cd backend
python main.py
```

```bash
cd backend
python -m pytest
```

```bash
cd frontend
npm run build
npm run lint
```

```bash
cd frontend
npm run test:chat-room-lifecycle
npm run test:friend-private-chat
```

## Git / Commit 规范

- 不提交无关文件。
- 不回滚用户工作区里的现有改动。
- 不使用 `git reset --hard`、`git checkout --` 这类破坏性操作。
- 提交前先看 `git status` 和 `git diff`。
- 一次提交只解决一个主题。
- 提交信息建议使用 `feat:`、`fix:`、`refactor:`、`docs:`、`chore:` 前缀。
- PR 描述写清楚“改了什么 + 为什么 + 怎么验证”。

## 互通说明

- Claude Code 额外上下文见 [CLAUDE.md](./CLAUDE.md)。
- 修改本文件时，检查 `CLAUDE.md` 是否也需要同步。
